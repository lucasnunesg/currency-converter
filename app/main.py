import uvicorn
from fastapi import FastAPI

from app.api.v1 import routes
from app.api.v2 import routes as routes_v2

app = FastAPI(title="Currency Conversion")

app.include_router(routes.router)
app.include_router(routes_v2.router)


@app.get("/", tags=["V1"], name="Home")
def index():
    return "Server is running!"


if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8081, reload=True)
