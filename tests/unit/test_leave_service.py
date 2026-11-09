import importlib
import sys
import boto3
from boto3.dynamodb.conditions import Key
from moto import mock_aws
import pytest

TABLE_NAME = "TestTable"


@pytest.fixture
def leave_service(monkeypatch):
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
            ],
            BillingMode="PAY_PER_REQUEST",
        )
        sys.modules.pop("api.services.leave_service", None)
        module = importlib.import_module("api.services.leave_service")
        yield module
        sys.modules.pop("api.services.leave_service", None)


@pytest.fixture
def table(leave_service):
    return boto3.resource("dynamodb", region_name="us-east-1").Table(TABLE_NAME)


def items_for(table, employee_id: str) -> list[dict]:
    return table.query(KeyConditionExpression=Key("PK").eq(employee_id))["Items"]


def test_save_writes_leave_item_keyed_by_employee_and_start_date(leave_service, table):
    employee_id = "emp-001"
    start_date = "2026-07-06"
    data = {"endDate": "2026-07-10", "note": "Summer vacation"}

    leave_service.save(employee_id, start_date, data)

    items = items_for(table, employee_id)
    assert len(items) == 1
    assert items[0] == {
        "PK": employee_id,
        "SK": start_date,
        "employeeId": employee_id,
        "startDate": start_date,
        "endDate": "2026-07-10",
        "note": "Summer vacation",
    }


def test_save_defaults_note_to_empty_string_when_note_omitted(leave_service, table):
    employee_id = "emp-001"
    start_date = "2026-07-06"
    data = {"endDate": "2026-07-10"}

    leave_service.save(employee_id, start_date, data)

    items = items_for(table, employee_id)
    assert items[0]["note"] == ""


def test_save_twice_with_same_keys_overwrites_instead_of_duplicating(leave_service, table):
    employee_id = "emp-001"
    start_date = "2026-09-14"

    leave_service.save(employee_id, start_date, {"endDate": "2026-09-18", "note": "v1"})
    leave_service.save(employee_id, start_date, {"endDate": "2026-09-25", "note": "v2"})

    stored = items_for(table, employee_id)
    assert len(stored) == 1
    assert stored[0]["note"] == "v2"
    assert stored[0]["endDate"] == "2026-09-25"


def test_list_for_employee_without_month_returns_all_leave_sorted_by_start_date(
    leave_service,
):
    employee_id = "emp-002"
    leave_service.save(employee_id, "2026-09-01", {"endDate": "2026-09-05"})
    leave_service.save(employee_id, "2026-07-06", {"endDate": "2026-07-10"})
    leave_service.save(employee_id, "2026-08-03", {"endDate": "2026-08-07"})

    result = leave_service.list_for_employee(employee_id, None)

    assert [item["startDate"] for item in result] == [
        "2026-07-06",
        "2026-08-03",
        "2026-09-01",
    ]


def test_list_for_employee_with_month_returns_only_that_months_leave(leave_service):
    employee_id = "emp-003"
    leave_service.save(employee_id, "2026-07-06", {"endDate": "2026-07-10"})
    leave_service.save(employee_id, "2026-08-03", {"endDate": "2026-08-07"})
    leave_service.save(employee_id, "2026-07-20", {"endDate": "2026-07-24"})

    result = leave_service.list_for_employee(employee_id, "2026-07")

    assert [item["startDate"] for item in result] == ["2026-07-06", "2026-07-20"]


def test_list_for_employee_returns_empty_list_when_employee_has_no_leave(leave_service):
    result = leave_service.list_for_employee("emp-none", None)
    assert result == []

