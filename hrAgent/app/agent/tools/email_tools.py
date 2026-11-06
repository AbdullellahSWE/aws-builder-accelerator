import os
import boto3
from openai import OpenAI
from strands import tool
from model.load import get_openrouter_api_key

TOPIC_ARN = os.environ.get(
    "HR_EMAIL_TOPIC_ARN",
    "arn:aws:sns:us-east-1:194163347210:HrLeavePortalNotifications-HrEmailTopic915EFFDB-DtIXOm9nfBmV",
)
sns = boto3.client("sns")


@tool
def generate_leave_email(
    employee_name: str, start_date: str, end_date: str, reason: str = ""
) -> str:
    """Generate a polite time-off request email addressed to the HR department.

    Use this tool when a user asks you to draft, write, or generate an email
    requesting leave on behalf of an employee.

    Args:
        employee_name: Full name of the employee requesting time off.
        start_date: First day of leave, formatted YYYY-MM-DD.
        end_date: Last day of leave, formatted YYYY-MM-DD.
        reason: Optional reason for the time-off request.
    """
    prompt = (
        "Write a short, polite email from an employee to the HR department "
        "requesting time off. Address it to the HR team. Use these details:\n"
        f"- Employee name: {employee_name}\n"
        f"- First day off: {start_date}\n"
        f"- Last day off: {end_date}\n"
        f"- Reason: {reason or 'not given'}\n\n"
        "Return only the email text, starting with a subject line."
    )

    client = OpenAI(
        api_key=get_openrouter_api_key(),
        base_url="https://openrouter.ai/api/v1",
    )
    response = client.chat.completions.create(
        model="deepseek/deepseek-v4.1-flash-1017",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1000,
    )
    return response.choices[0].message.content


@tool
def send_email_to_hr(subject: str, body: str) -> dict:
    """Send an email to the HR department by publishing it to the HR SNS topic.

    Use this tool when a user asks you to send an email you have drafted to HR.
    Anyone subscribed to the topic (for example an HR mailbox) receives it.

    Args:
        subject: The email subject line.
        body: The email body text.
    """
    response = sns.publish(TopicArn=TOPIC_ARN, Subject=subject, Message=body)
    return {"messageId": response["MessageId"]}
