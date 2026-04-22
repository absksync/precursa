from fastapi import FastAPI
from app.api.routes import router

app = FastAPI(title="Precursa API")

app.include_router(router)

@app.get("/")
def root():
    return {"message": "Precursa backend running"}