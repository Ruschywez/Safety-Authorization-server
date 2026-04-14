from src.routers import *
from fastapi import FastAPI

app = FastAPI()
app.include_router(router)