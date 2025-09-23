from fastapi import FastAPI
from .database import engine
from .models import Base
from .routers import whatsapp

# Crea tablas en DB
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Whats Scheduler")

app.include_router(whatsapp.router)