from sqlalchemy import Column, Integer, String, DateTime
from .database import Base
from datetime import datetime

class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    client_name = Column(String, index=True)
    service = Column(String)  # Ej. "masaje", "facial"
    date_time = Column(DateTime)
    status = Column(String, default="pending")  # pending, confirmed, cancelled
    created_at = Column(DateTime, default=datetime.utcnow)