from aws_cdk import (
    Aws,
    CfnOutput,
    RemovalPolicy,
    Stack,
    aws_bedrock as bedrock,
    aws_cognito as cognito,
    aws_dynamodb as dynamodb,
    aws_iam as iam,
    aws_sns as sns,
    aws_ssm as ssm,
)
from cdk_nag import NagSuppressions
from constructs import Construct

WORKFLOW_MODEL_ID = "us.anthropic.claude-haiku-4-5-20251001-v1:0"

class AgentRuntimeStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        table: dynamodb.Table,
        hr_email_topic: sns.Topic,
        user_pool: cognito.UserPool,
        user_pool_client: cognito.UserPoolClient,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # 1. IAM Execution Role for Bedrock Agent
        execution_role = iam.Role(
            self,
            "HrAgentRuntimeExecutionRole",
            assumed_by=iam.ServicePrincipal("bedrock.amazonaws.com"),
        )

        # DynamoDB permissions
        table.grant_read_write_data(execution_role)

        # SNS Publish permissions
        hr_email_topic.grant_publish(execution_role)

        # Bedrock Model Invocation permissions
        execution_role.add_to_policy(
            iam.PolicyStatement(
                actions=["bedrock:InvokeModel"],
                resources=[
                    f"arn:aws:bedrock:{Aws.REGION}:{Aws.ACCOUNT_ID}:"
                    f"inference-profile/{WORKFLOW_MODEL_ID}",
                    "arn:aws:bedrock:*::foundation-model/anthropic.claude-haiku-4-5-20251001-v1:0",
                    "arn:aws:bedrock:*::foundation-model/anthropic.claude-sonnet-5",
                ],
            )
        )

        # CloudWatch Logging permissions for Agent Runtime
        execution_role.add_to_policy(
            iam.PolicyStatement(
                actions=[
                    "logs:CreateLogGroup",
                    "logs:CreateLogStream",
                    "logs:PutLogEvents",
                ],
                resources=[
                    f"arn:aws:logs:{Aws.REGION}:{Aws.ACCOUNT_ID}:log-group:/aws/bedrock-agentcore/runtimes/*",
                    f"arn:aws:logs:{Aws.REGION}:{Aws.ACCOUNT_ID}:log-group:*",
                ],
            )
        )

        # SSM Parameter Store Access
        execution_role.add_to_policy(
            iam.PolicyStatement(
                actions=["ssm:GetParameter", "ssm:GetParameters"],
                resources=[
                    f"arn:aws:ssm:{Aws.REGION}:{Aws.ACCOUNT_ID}:parameter/hr-leave-portal/*"
                ],
            )
        )

        # 2. Amazon Bedrock Guardrail
        guardrail = bedrock.CfnGuardrail(
            self,
            "HrAgentGuardrail",
            name="hr-agent-guardrail",
            blocked_input_messaging="I can't help with that request.",
            blocked_outputs_messaging="I can't share that.",
            sensitive_information_policy_config=bedrock.CfnGuardrail.SensitiveInformationPolicyConfigProperty(
                pii_entities_config=[
                    bedrock.CfnGuardrail.PiiEntityConfigProperty(type="EMAIL", action="ANONYMIZE"),
                    bedrock.CfnGuardrail.PiiEntityConfigProperty(type="PHONE", action="ANONYMIZE"),
                    bedrock.CfnGuardrail.PiiEntityConfigProperty(type="US_SOCIAL_SECURITY_NUMBER", action="BLOCK"),
                ]
            ),
            content_policy_config=bedrock.CfnGuardrail.ContentPolicyConfigProperty(
                filters_config=[
                    bedrock.CfnGuardrail.ContentFilterConfigProperty(
                        type="PROMPT_ATTACK",
                        input_strength="HIGH",
                        output_strength="NONE"
                    ),
                ]
            ),
        )

        # Grant execution role permission to apply the guardrail
        execution_role.add_to_policy(
            iam.PolicyStatement(
                actions=["bedrock:ApplyGuardrail"],
                resources=[guardrail.attr_guardrail_arn]
            )
        )

        self.execution_role = execution_role
        self.guardrail_id = guardrail.attr_guardrail_id
        self.guardrail_version = guardrail.attr_version

        # cdk-nag suppressions placed inside __init__
        NagSuppressions.add_stack_suppressions(
            self,
            [
                {
                    "id": "AwsSolutions-IAM5",
                    "reason": "Agent runtime execution role requires wildcard permissions for logging, SSM parameters, and Bedrock foundation/inference models.",
                }
            ],
        )