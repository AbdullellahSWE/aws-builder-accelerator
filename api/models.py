from datetime import date

from pydantic import BaseModel

<<<<<<< HEAD

=======
>>>>>>> deployToLambda
class EmployeeIn(BaseModel):
    name: str
    department: str
    startDate: date
    role: str = "employee"