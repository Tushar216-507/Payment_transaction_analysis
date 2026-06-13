from fastapi import FastAPI
from api.jobs import router

app = FastAPI(
    title="Payment Transaction Analysis"
)

app.include_router(router)


@app.get("/")
def home():
    return {
        "message":
        "Payment Transaction Analysis API"
    }