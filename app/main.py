from fastapi import FastAPI
import uvicorn
from api.v1 import routes
from database import init_databases, update_conversion_collection

app = FastAPI(title="Currency Conversion")

app.include_router(routes.router)


@app.get("/")
def index():
    return "Server is running!"


if __name__ == "__main__":

    """[currency_rate_collection, tracked_currencies_collection] = init_databases()
    update_conversion_collection(
        rate_coll=currency_rate_collection, track_coll=tracked_currencies_collection
    )"""
    uvicorn.run("main:app", host="localhost", port=8081, reload=True)
