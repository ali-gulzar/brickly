from fastapi import FastAPI
from mangum import Mangum

from services.database import engine
from models.database import Base

import controllers.user as user_controller

app = FastAPI()

app.include_router(user_controller.router, prefix="/user", tags=["user"])

handler = Mangum(app)
