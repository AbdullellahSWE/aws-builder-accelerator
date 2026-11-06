import os
from strands.models.openai import OpenAIModel


def get_openrouter_api_key() -> str:
    key = os.getenv("OPENROUTER_API_KEY", "")
    if not key:
        try:
            import boto3

            ssm = boto3.client("ssm", region_name="us-east-1")
            param = ssm.get_parameter(
                Name="/hr-leave-portal/openrouter-api-key", WithDecryption=True
            )
            key = param["Parameter"]["Value"]
        except Exception:
            key = ""
    return key


def load_model() -> OpenAIModel:
    """Get model client pointing to OpenRouter."""
    api_key = get_openrouter_api_key()
    return OpenAIModel(
        client_args={
            "api_key": api_key,
            "base_url": "https://openrouter.ai/api/v1",
        },
        model_id="deepseek/deepseek-v4.1-flash-1017",
        params={
            "max_tokens": 2048,
            "temperature": 0.3,
        },
    )
