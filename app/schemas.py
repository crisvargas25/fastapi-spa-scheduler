from pydantic import BaseModel
from datetime import datetime

class AppointmentCreate(BaseModel):
    client_name: str
    service: str
    date_time: datetime

class AppointmentResponse(BaseModel):
    id: int
    client_name: str
    service: str
    date_time: datetime
    status: str
    created_at: datetime

    class Config:
        from_attributes = True  # Para mapear desde ORM