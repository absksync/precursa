from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router
from app.core.startup import start_ais_stream

app = FastAPI(title="Precursa API")

# ✅ CORS FIX
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # for hackathon (later restrict)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/")
def root():
    return {"message": "Precursa backend running"}


@app.on_event("startup")
async def startup_event():
    await start_ais_stream()