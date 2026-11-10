from aws_cdk import (
    Acknowledgment,
    CfnOutput,
    Duration,
    RemovalPolicy,
    Stack,
    Validations,
    aws_apigateway as apigw,
    aws_cognito as cognito,
    aws_dynamodb as dynamodb,
    aws_iam as iam,
    aws_lambda as lambda_,
)
from cdk_nag import NagSuppressions
from constructs import Construct


class BackendStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        ui_origin: str | None = None,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        table = dynamodb.Table(
            self,
            "HrTable",
            partition_key=dynamodb.Attribute(
                name="PK", type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="SK", type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            encryption=dynamodb.TableEncryption.AWS_MANAGED,
            point_in_time_recovery_specification=dynamodb.PointInTimeRecoverySpecification(
                point_in_time_recovery_enabled=True
            ),
            removal_policy=RemovalPolicy.DESTROY,
        )

        table.add_global_secondary_index(
            index_name="GSI1",
            partition_key=dynamodb.Attribute(
                name="GSI1PK", type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="GSI1SK", type=dynamodb.AttributeType.STRING
            ),
        )

        fastapi_layer = lambda_.LayerVersion(
            self,
            "FastApiLayer",
            code=lambda_.Code.from_asset("scripts/fastapi-layer.zip"),
            compatible_runtimes=[lambda_.Runtime.PYTHON_3_14],
            description="fastapi, pydantic, mangum, powertools for the HR API",
        )

        lambda_env = {
            "TABLE_NAME": table.table_name,
            "POWERTOOLS_SERVICE_NAME": "hr-api",
            "POWERTOOLS_LOG_LEVEL": "INFO",
        }
        if ui_origin:
            lambda_env["UI_ORIGIN"] = ui_origin

        api_function = lambda_.Function(
            self,
            "ApiFunction",
            runtime=lambda_.Runtime.PYTHON_3_14,
            handler="handler.lambda_handler",
            code=lambda_.Code.from_asset("api", exclude=["__pycache__", "*.pyc"]),
            layers=[fastapi_layer],
            timeout=Duration.seconds(10),
            memory_size=512,
            environment=lambda_env,
            tracing=lambda_.Tracing.ACTIVE,
        )

        self.api_function = api_function
        self.table = table

        self.api_function.add_to_role_policy(
            iam.PolicyStatement(
                actions=[
                    "dynamodb:PutItem",
                    "dynamodb:GetItem",
                    "dynamodb:Query",
                    "dynamodb:DeleteItem",
                ],
                resources=[self.table.table_arn, f"{self.table.table_arn}/index/*"],
            )
        )

        self.user_pool = cognito.UserPool(
            self,
            "HrUserPool",
            self_sign_up_enabled=False,
            sign_in_aliases=cognito.SignInAliases(email=True),
            password_policy=cognito.PasswordPolicy(
                min_length=8,
                require_lowercase=True,
                require_uppercase=True,
                require_digits=True,
                require_symbols=True,
            ),
            removal_policy=RemovalPolicy.DESTROY,
        )

        self.user_pool_client = self.user_pool.add_client(
            "HrUserPoolClient",
            auth_flows=cognito.AuthFlow(user_password=True, user_srp=True),
        )

        authorizer = apigw.CognitoUserPoolsAuthorizer(
            self, "HrAuthorizer", cognito_user_pools=[self.user_pool]
        )

        allowed_origins = ["http://localhost:5173"]
        if ui_origin:
            allowed_origins.append(ui_origin)

        self.api = apigw.LambdaRestApi(
            self,
            "HrApi",
            handler=api_function,
            default_cors_preflight_options=apigw.CorsOptions(
                allow_origins=allowed_origins,
                allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                allow_headers=[
                    "Content-Type",
                    "X-Amz-Date",
                    "Authorization",
                    "X-Api-Key",
                    "X-Amz-Security-Token",
                ],
            ),
            default_method_options=apigw.MethodOptions(
                authorization_type=apigw.AuthorizationType.COGNITO,
                authorizer=authorizer,
            ),
        )

        CfnOutput(self, "ApiUrl", value=self.api.url)
        CfnOutput(self, "TableName", value=table.table_name)
        CfnOutput(self, "UserPoolId", value=self.user_pool.user_pool_id)
        CfnOutput(
            self, "UserPoolClientId", value=self.user_pool_client.user_pool_client_id
        )

        # Findings we've read and decided to accept. Keep them last so they're
        # easy to find, and never add one without a reason.
        Validations.of(self).acknowledge(
            Acknowledgment(
                id="AwsSolutions::AwsSolutions-COG2",
                reason="WORKSHOP ONLY. MFA is not enabled to keep sign-in to one step. A real "
                       "HR system must enable it, see /security/conclusion/.",
            ),
            Acknowledgment(
                id="AwsSolutions::AwsSolutions-APIG4",
                reason="Fires on CORS preflight OPTIONS methods, which must be unauthenticated. "
                       "Every other method inherits the Cognito authorizer through "
                       "default_method_options.",
            ),
        )

        # cdk-nag suppressions for Backend Stack
        NagSuppressions.add_resource_suppressions(
            api_function.role,
            [
                {
                    "id": "AwsSolutions-IAM4",
                    "reason": "AWSLambdaBasicExecutionRole is standard for Lambda logging.",
                },
                {
                    "id": "AwsSolutions-IAM5",
                    "reason": "Lambda requires wildcard permissions for X-Ray tracing and DynamoDB GSI indexes.",
                },
            ],
            apply_to_children=True,
        )

        NagSuppressions.add_resource_suppressions(
            self.user_pool,
            [
                {
                    "id": "AwsSolutions-COG2",
                    "reason": "MFA is omitted for workshop environment simplicity.",
                },
                {
                    "id": "AwsSolutions-COG8",
                    "reason": "UserPool Plus tier is not required for workshop environment.",
                },
            ],
        )

        NagSuppressions.add_resource_suppressions(
            self.api,
            [
                {
                    "id": "AwsSolutions-APIG1",
                    "reason": "API Gateway access logging omitted for workshop simplicity.",
                },
                {
                    "id": "AwsSolutions-APIG2",
                    "reason": "Request validation is handled in FastAPI application code.",
                },
                {
                    "id": "AwsSolutions-APIG3",
                    "reason": "WAF on REST API stage omitted for workshop simplicity.",
                },
                {
                    "id": "AwsSolutions-APIG6",
                    "reason": "CloudWatch execution logging on REST API stage omitted for workshop simplicity.",
                },
            ],
            apply_to_children=True,
        )