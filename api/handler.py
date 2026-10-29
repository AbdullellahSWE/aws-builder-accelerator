from fastapi import FastAPI
<<<<<<< HEAD
=======
from mangum import Mangum
>>>>>>> deployToLambda

from controllers import employee_controller

app = FastAPI(title="HR Leave Portal")

<<<<<<< HEAD
app.include_router(employee_controller.router)
=======
app.include_router(employee_controller.router)

lambda_handler = Mangum(app)
>>>>>>> deployToLambda
