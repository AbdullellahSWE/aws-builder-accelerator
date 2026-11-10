from aws_cdk import (
    CfnOutput,
    Duration,
    RemovalPolicy,
    Stack,
    aws_cloudfront as cloudfront,
    aws_cloudfront_origins as origins,
    aws_s3 as s3,
    aws_s3_deployment as s3deploy,
    aws_wafv2 as wafv2,
)
from cdk_nag import NagSuppressions
from constructs import Construct


class UiStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        bucket = s3.Bucket(
            self,
            "UiBucket",
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            encryption=s3.BucketEncryption.S3_MANAGED,
            enforce_ssl=True,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
        )

        web_acl = wafv2.CfnWebACL(
            self,
            "UiWebAcl",
            scope="CLOUDFRONT",
            default_action=wafv2.CfnWebACL.DefaultActionProperty(allow={}),
            visibility_config=wafv2.CfnWebACL.VisibilityConfigProperty(
                cloud_watch_metrics_enabled=True,
                metric_name="UiWebAcl",
                sampled_requests_enabled=True,
            ),
            rules=[
                wafv2.CfnWebACL.RuleProperty(
                    name="AWSManagedRulesCommonRuleSet",
                    priority=0,
                    statement=wafv2.CfnWebACL.StatementProperty(
                        managed_rule_group_statement=wafv2.CfnWebACL.ManagedRuleGroupStatementProperty(
                            vendor_name="AWS",
                            name="AWSManagedRulesCommonRuleSet",
                        )
                    ),
                    override_action=wafv2.CfnWebACL.OverrideActionProperty(none={}),
                    visibility_config=wafv2.CfnWebACL.VisibilityConfigProperty(
                        cloud_watch_metrics_enabled=True,
                        metric_name="CommonRuleSet",
                        sampled_requests_enabled=True,
                    ),
                ),
            ],
        )

        distribution = cloudfront.Distribution(
            self,
            "UiDistribution",
            default_root_object="index.html",
            web_acl_id=web_acl.attr_arn,
            default_behavior=cloudfront.BehaviorOptions(
                origin=origins.S3BucketOrigin.with_origin_access_control(bucket),
                viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                response_headers_policy=cloudfront.ResponseHeadersPolicy.SECURITY_HEADERS,
            ),
            error_responses=[
                cloudfront.ErrorResponse(
                    http_status=403,
                    response_http_status=200,
                    response_page_path="/index.html",
                    ttl=Duration.seconds(0),
                ),
                cloudfront.ErrorResponse(
                    http_status=404,
                    response_http_status=200,
                    response_page_path="/index.html",
                    ttl=Duration.seconds(0),
                ),
            ],
        )

        s3deploy.BucketDeployment(
            self,
            "UiDeployment",
            sources=[s3deploy.Source.asset("ui/dist")],
            destination_bucket=bucket,
            distribution=distribution,
            distribution_paths=["/*"],
        )

        CfnOutput(
            self,
            "DistributionDomainName",
            value=distribution.distribution_domain_name,
        )
        CfnOutput(
            self,
            "UiUrl",
            value=f"https://{distribution.distribution_domain_name}",
        )

        # Nag Suppressions for UI Stack
        NagSuppressions.add_resource_suppressions(
            bucket,
            [
                {
                    "id": "AwsSolutions-S1",
                    "reason": "S3 server access logging disabled for workshop static site bucket.",
                }
            ],
        )

        NagSuppressions.add_resource_suppressions(
            distribution,
            [
                {
                    "id": "AwsSolutions-CFR1",
                    "reason": "Geo restriction not required for workshop UI.",
                },
                {
                    "id": "AwsSolutions-CFR3",
                    "reason": "CloudFront access logging omitted for workshop simplicity.",
                },
                {
                    "id": "AwsSolutions-CFR4",
                    "reason": "Default CloudFront viewer certificate uses default TLS settings.",
                },
            ],
        )

        # Suppress cdk-nag findings on CDK internal BucketDeployment custom resource
        NagSuppressions.add_stack_suppressions(
            self,
            [
                {
                    "id": "AwsSolutions-IAM4",
                    "reason": "CDK BucketDeployment construct uses managed policies internally.",
                },
                {
                    "id": "AwsSolutions-IAM5",
                    "reason": "CDK BucketDeployment construct requires S3 wildcard permissions.",
                },
                {
                    "id": "AwsSolutions-L1",
                    "reason": "CDK BucketDeployment custom resource runtime managed by AWS CDK library.",
                },
            ],
        )