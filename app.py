#!/usr/bin/env python3
import aws_cdk as cdk
import cdk_nag
# from aws_cdk import Validations
from cdk_nag import AwsSolutionsChecks

from hr_leave_portal.agent_runtime_stack import AgentRuntimeStack
from hr_leave_portal.backend_stack import BackendStack
from hr_leave_portal.dashboard_stack import DashboardStack
from hr_leave_portal.notification_stack import NotificationStack
from hr_leave_portal.state_machine_stack import StateMachineStack
from hr_leave_portal.ui_stack import UiStack

app = cdk.App()


# Validations.of(app).add_plugins(AwsSolutionsChecks(app, verbose=True))



env = cdk.Environment(
    account="194163347210",
    region="us-east-1"
)

notifications = NotificationStack(app, "HrLeavePortalNotifications", env=env)

ui_origin = app.node.try_get_context("uiOrigin")

backend = BackendStack(
    app,
    "HrLeavePortalBackend",
    ui_origin=ui_origin,
    env=env,
)

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

DashboardStack(
    app,
    "HrLeavePortalDashboard",
    api_function=backend.api_function,
    api=backend.api,
    env=env,
)

# Attach cdk-nag security checks across all stacks
cdk.Aspects.of(app).add(cdk_nag.AwsSolutionsChecks(verbose=True))

app.synth()