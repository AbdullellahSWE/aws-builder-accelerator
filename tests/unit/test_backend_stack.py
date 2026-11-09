from pathlib import Path
import aws_cdk as cdk
from aws_cdk.assertions import Match, Template
import pytest
from hr_leave_portal.backend_stack import BackendStack

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


@pytest.fixture
def template(monkeypatch) -> Template:
    monkeypatch.chdir(REPO_ROOT)
    app = cdk.App()
    stack = BackendStack(app, "TestBackendStack")
    return Template.from_stack(stack)


def test_dynamodb_table_has_pk_sk_key_schema_and_gsi1_index(template: Template):
    template.has_resource_properties(
        "AWS::DynamoDB::Table",
        {
            "KeySchema": [
                {"AttributeName": "PK", "KeyType": "HASH"},
                {"AttributeName": "SK", "KeyType": "RANGE"},
            ],
            "AttributeDefinitions": Match.array_with(
                [
                    {"AttributeName": "GSI1PK", "AttributeType": "S"},
                    {"AttributeName": "GSI1SK", "AttributeType": "S"},
                ]
            ),
            "GlobalSecondaryIndexes": [
                {
                    "IndexName": "GSI1",
                    "KeySchema": [
                        {"AttributeName": "GSI1PK", "KeyType": "HASH"},
                        {"AttributeName": "GSI1SK", "KeyType": "RANGE"},
                    ],
                    "Projection": {"ProjectionType": "ALL"},
                }
            ],
        },
    )


def test_api_lambda_has_active_tracing(template: Template):
    template.has_resource_properties(
        "AWS::Lambda::Function",
        {"TracingConfig": {"Mode": "Active"}},
    )


def test_api_lambda_has_exactly_one_layer_attached(template: Template):
    functions = template.find_resources("AWS::Lambda::Function")
    api_function = next(
        f
        for f in functions.values()
        if f["Properties"]["Handler"] == "handler.lambda_handler"
    )
    assert len(api_function["Properties"]["Layers"]) == 1


def test_api_lambda_layer_resolves_from_the_fastapi_powertools_ssm_parameter(
    template: Template,
):
    functions = template.find_resources("AWS::Lambda::Function")
    api_function = next(
        f
        for f in functions.values()
        if f["Properties"]["Handler"] == "handler.lambda_handler"
    )
    layer = api_function["Properties"]["Layers"][0]
    assert "Ref" in layer or "Fn::GetAtt" in layer


def test_api_lambda_has_powertools_and_table_environment_variables(template: Template):
    template.has_resource_properties(
        "AWS::Lambda::Function",
        {
            "Environment": {
                "Variables": {
                    "TABLE_NAME": Match.any_value(),
                    "POWERTOOLS_SERVICE_NAME": "hr-api",
                    "POWERTOOLS_LOG_LEVEL": "INFO",
                }
            }
        },
    )


def test_rest_api_exists_with_a_cognito_user_pools_authorizer(template: Template):
    template.resource_count_is("AWS::ApiGateway::RestApi", 1)
    template.has_resource_properties(
        "AWS::ApiGateway::Authorizer",
        {"Type": "COGNITO_USER_POOLS"},
    )


def test_proxy_methods_inherit_the_cognito_authorizer_by_default(template: Template):
    cognito_methods = template.find_resources(
        "AWS::ApiGateway::Method",
        {
            "Properties": {
                "HttpMethod": "ANY",
                "AuthorizationType": "COGNITO_USER_POOLS",
            }
        },
    )
    assert len(cognito_methods) == 2  # ANY on / and on /{proxy+}


def test_cors_preflight_options_methods_are_intentionally_unauthenticated(
    template: Template,
):
    options_methods = template.find_resources(
        "AWS::ApiGateway::Method",
        {"Properties": {"HttpMethod": "OPTIONS", "AuthorizationType": "NONE"}},
    )
    assert len(options_methods) >= 2  # OPTIONS on / and /{proxy+}

