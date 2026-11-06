#!/usr/bin/env python3
import aws_cdk as cdk
from hr_leave_portal.agent_runtime_stack import AgentRuntimeStack
from hr_leave_portal.backend_stack import BackendStack
from hr_leave_portal.notification_stack import NotificationStack
from hr_leave_portal.state_machine_stack import StateMachineStack
from hr_leave_portal.ui_stack import UiStack

app = cdk.App()

# Explicitly define target environment for the new AWS account
env = cdk.Environment(
    account="194163347210",
    region="us-east-1"
)

notifications = NotificationStack(app, "HrLeavePortalNotifications", env=env)
backend = BackendStack(app, "HrLeavePortalBackend", env=env)

StateMachineStack(
    app,
    "HrLeavePortalStateMachine",
    hr_email_topic=notifications.hr_email_topic,
    api_function=backend.api_function,
    env=env,
)

AgentRuntimeStack(
    app,
    "HrLeavePortalAgentRuntime",
    table=backend.table,
    hr_email_topic=notifications.hr_email_topic,
    user_pool=backend.user_pool,
    user_pool_client=backend.user_pool_client,
    env=env,
)

UiStack(app, "HrLeavePortalUi", env=env)

app.synth()
