import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    AIS_API_KEY = os.getenv("AIS_API_KEY")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

settings = Settings()