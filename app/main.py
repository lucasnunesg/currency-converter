from fastapi import FastAPI
import uvicorn
from app.api.v1 import routes

app = FastAPI(title="Currency Conversion")

app.include_router(routes.router)


@app.get("/")
def index():
    return "Server is running!"


if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8081, reload=True)
