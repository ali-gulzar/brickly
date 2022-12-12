from fastapi import FastAPI
from mangum import Mangum

import controllers.user as user_controller
import controllers.house as house_controller

app = FastAPI()

app.include_router(user_controller.router, prefix="/user", tags=["user"])
app.include_router(house_controller.router, prefix="/house", tags=["house"])

handler = Mangum(app)
