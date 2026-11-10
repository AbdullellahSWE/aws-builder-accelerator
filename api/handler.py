import os
from aws_lambda_powertools import Logger, Tracer
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum

from controllers import employee_controller, hr_request_controller, leave_controller

logger = Logger()
tracer = Tracer()

app = FastAPI(title="HR Leave Portal")

# Pin CORS to local Vite dev server and deployed CloudFront UI
allowed_origins = ["http://localhost:5173"]
if os.environ.get("UI_ORIGIN"):
    allowed_origins.append(os.environ["UI_ORIGIN"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(employee_controller.router)
app.include_router(leave_controller.router)
app.include_router(hr_request_controller.router)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info("request received", method=request.method, path=request.url.path)
    response = await call_next(request)
    logger.info("request completed", status_code=response.status_code)
    return response


@logger.inject_lambda_context
@tracer.capture_lambda_handler
def lambda_handler(event, context):
    return Mangum(app)(event, context)