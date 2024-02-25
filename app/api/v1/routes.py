from fastapi import APIRouter

router = APIRouter(prefix="/v1", tags=["V1"])


@router.get("/")
def index():
    return {"message": "Hello World"}
