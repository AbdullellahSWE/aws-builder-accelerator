import importlib
import sys
import boto3
from moto import mock_aws
import pytest

TABLE_NAME = "TestTable"


@pytest.fixture
def employee_service(monkeypatch):
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "testing")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "testing")
    monkeypatch.setenv("AWS_SECURITY_TOKEN", "testing")
    monkeypatch.setenv("AWS_SESSION_TOKEN", "testing")
    monkeypatch.setenv("AWS_DEFAULT_REGION", "us-east-1")
    monkeypatch.setenv("TABLE_NAME", TABLE_NAME)
    with mock_aws():
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        dynamodb.create_table(
            TableName=TABLE_NAME,
            KeySchema=[
                {"AttributeName": "PK", "KeyType": "HASH"},
                {"AttributeName": "SK", "KeyType": "RANGE"},
            ],
            AttributeDefinitions=[
                {"AttributeName": "PK", "AttributeType": "S"},
                {"AttributeName": "SK", "AttributeType": "S"},
                {"AttributeName": "GSI1PK", "AttributeType": "S"},
                {"AttributeName": "GSI1SK", "AttributeType": "S"},
            ],
            GlobalSecondaryIndexes=[
                {
                    "IndexName": "GSI1",
                    "KeySchema": [
                        {"AttributeName": "GSI1PK", "KeyType": "HASH"},
                        {"AttributeName": "GSI1SK", "KeyType": "RANGE"},
                    ],
                    "Projection": {"ProjectionType": "ALL"},
                }
            ],
            BillingMode="PAY_PER_REQUEST",
        )
        sys.modules.pop("api.services.employee_service", None)
        module = importlib.import_module("api.services.employee_service")
        yield module
        sys.modules.pop("api.services.employee_service", None)


@pytest.fixture
def table(employee_service):
    return boto3.resource("dynamodb", region_name="us-east-1").Table(TABLE_NAME)


def test_create_generates_eight_character_id_used_as_sort_key(employee_service):
    data = {
        "name": "Grace Hopper",
        "department": "Engineering",
        "startDate": "2024-01-15",
        "role": "admin",
    }
    item = employee_service.create(data)

    assert item["PK"] == "USER"
    assert len(item["employeeId"]) == 8
    assert item["SK"] == item["employeeId"]


def test_create_called_twice_generates_two_different_ids(employee_service):
    data = {
        "name": "Grace Hopper",
        "department": "Engineering",
        "startDate": "2024-01-15",
    }
    first = employee_service.create(data)
    second = employee_service.create(data)

    assert first["SK"] != second["SK"]


def test_save_writes_expected_item_to_table(employee_service, table):
    data = {
        "name": "Alan Turing",
        "department": "Research",
        "startDate": "2023-06-01",
        "role": "scientist",
    }
    employee_id = "alan1234"
    saved = employee_service.save(employee_id, data)

    response = table.get_item(Key={"PK": "USER", "SK": employee_id})
    stored = response.get("Item")

    assert stored == {
        "PK": "USER",
        "SK": employee_id,
        "GSI1PK": "USER_BY_DATE",
        "GSI1SK": "2023-06-01",
        "employeeId": employee_id,
        "name": "Alan Turing",
        "department": "Research",
        "startDate": "2023-06-01",
        "role": "scientist",
    }
    assert saved == stored


def test_save_defaults_role_to_employee_when_role_omitted(employee_service, table):
    data = {
        "name": "Ada Lovelace",
        "department": "Engineering",
        "startDate": "2024-05-10",
    }
    employee_id = "ada56789"
    saved = employee_service.save(employee_id, data)

    assert saved["role"] == "employee"
    response = table.get_item(Key={"PK": "USER", "SK": employee_id})
    assert response["Item"]["role"] == "employee"

