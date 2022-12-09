from fastapi import FastAPI
from mangum import Mangum

import controllers.users as users_controller

app = FastAPI()

app.include_router(users_controller.router, prefix="/users", tags=["users"])

handler = Mangum(app)
