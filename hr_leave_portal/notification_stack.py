from aws_cdk import (
    Stack,
    aws_kms as kms,
    aws_sns as sns,
    aws_sns_subscriptions as sns_subscriptions,
)
from constructs import Construct


class NotificationStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Validate that context parameter hrEmail is passed during synth/deploy
        hr_email_address = self.node.try_get_context("hrEmail")
        if not hr_email_address:
            raise ValueError(
                "Missing required context value: hrEmail. "
                "Deploy with: cdk deploy --all -c hrEmail=you@example.com"
            )

        # Encrypt topic with AWS managed key for SNS
        self.hr_email_topic = sns.Topic(
            self,
            "HrEmailTopic",
            master_key=kms.Alias.from_alias_name(self, "SnsKey", "alias/aws/sns"),
        )

        self.hr_email_topic.add_subscription(
            sns_subscriptions.EmailSubscription(hr_email_address)
        )