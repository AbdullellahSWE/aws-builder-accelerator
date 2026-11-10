from aws_cdk import (
    Aws,
    CfnOutput,
    RemovalPolicy,
    Stack,
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

        # IAM Execution Role for Bedrock Agent
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

        self.execution_role = execution_role

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