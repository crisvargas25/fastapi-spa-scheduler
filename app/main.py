from fastapi import FastAPI
from .database import engine
from .models import Base
from .routers import appointments

# Crea tablas en DB
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Spa Scheduler")

app.include_router(appointments.router)