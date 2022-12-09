from fastapi import APIRouter

router = APIRouter()

@router.post("")
def create_user():
    return "Creating user second time"
