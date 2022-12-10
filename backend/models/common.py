from pydantic import BaseModel

class ErrorMessage(BaseModel):
    status_code: str
    message: str