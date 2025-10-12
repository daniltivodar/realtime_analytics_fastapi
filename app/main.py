from fastapi import FastAPI
from dotenv import load_dotenv

from app.core.config import settings

from app.api.routers import main_router

load_dotenv()

app = FastAPI(title=settings.app_title)
app.include_router(main_router)
