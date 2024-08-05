from fastapi import FastAPI

from app.core.database import lifespan

app = FastAPI(lifespan=lifespan)
