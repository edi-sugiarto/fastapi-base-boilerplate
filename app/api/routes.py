from fastapi import APIRouter

router = APIRouter()

# Include task endpoints with prefix
# router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])


@router.get("/hello")
async def hello_world():
    return {"message": "Hello, world!"}


@router.get("/items/{item_id}")
async def read_item(item_id: int):
    return {"item_id": item_id}
