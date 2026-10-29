import os
import aws_cdk as cdk
from hr_leave_portal.backend_stack import BackendStack

app = cdk.App()

BackendStack(
    app,
    "HrLeavePortalBackend",
    env=cdk.Environment(
        account=os.getenv("CDK_DEFAULT_ACCOUNT", "136658063017"),
        region=os.getenv("CDK_DEFAULT_REGION", "us-east-1"),
    ),
)

app.synth()