import uvicorn
from fastapi import FastAPI

from app.api.v1 import routes

app = FastAPI(title="Currency Conversion")

app.include_router(routes.router)


@app.get("/", tags=["V1"], name="Home")
def index():
    return "Server is running!"


if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8081, reload=True)
