from fastapi import FastAPI
from .app.database import engine
from .app.models import Base
from .app.routers import appointments

# Crea tablas en DB
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Spa Scheduler")

app.include_router(appointments.router)