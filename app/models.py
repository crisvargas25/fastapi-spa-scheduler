from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime

class Service(Base):
    __tablename__ = "services"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)  # Ej. "Masaje Sueco Anti Estrés"

    reservable_services = relationship("ReservableService", back_populates="service")
    availability_policies = relationship("AvailabilityPolicy", back_populates="service")
    appointments = relationship("Appointment", back_populates="service")

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)  # Ej. "Té verde"
    price = Column(Float)  # Ej. 20.0

class Reservable(Base):
    __tablename__ = "reservables"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)  # Ej. "Fanny Cervantes"

    reservable_services = relationship("ReservableService", back_populates="reservable")
    schedule_policies = relationship("SchedulePolicy", back_populates="reservable")
    appointments = relationship("Appointment", back_populates="reservable")

class ReservableService(Base):
    __tablename__ = "reservable_services"

    id = Column(Integer, primary_key=True, index=True)
    reservable_id = Column(Integer, ForeignKey("reservables.id"))
    service_id = Column(Integer, ForeignKey("services.id"))

    reservable = relationship("Reservable", back_populates="reservable_services")
    service = relationship("Service", back_populates="reservable_services")

class SchedulePolicy(Base):
    __tablename__ = "schedule_policies"

    id = Column(Integer, primary_key=True, index=True)
    reservable_id = Column(Integer, ForeignKey("reservables.id"))
    service_id = Column(Integer, ForeignKey("services.id"), nullable=True)  # Opcional si aplica a todos
    rrule = Column(String)  # Ej. "FREQ=WEEKLY;BYDAY=MO,TU,WE;BYHOUR=9,10,11,12"

    reservable = relationship("Reservable", back_populates="schedule_policies")

class AvailabilityPolicy(Base):
    __tablename__ = "availability_policies"

    id = Column(Integer, primary_key=True, index=True)
    service_id = Column(Integer, ForeignKey("services.id"))
    rrule = Column(String)  # Ej. "FREQ=WEEKLY;BYDAY=SU;BYHOUR=9,10,11,12,13,14"

    service = relationship("Service", back_populates="availability_policies")

class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    client_name = Column(String, index=True)
    client_phone = Column(String)  # Nuevo: Número de WhatsApp para trackear
    service_id = Column(Integer, ForeignKey("services.id"))
    reservable_id = Column(Integer, ForeignKey("reservables.id"), nullable=True)
    date_time = Column(DateTime)
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)

    service = relationship("Service", back_populates="appointments")
    reservable = relationship("Reservable", back_populates="appointments")

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String, unique=True)  # Número de WhatsApp
    state = Column(String, default="start")  # Ej. "start", "choose_service", "choose_date", "confirm"
    data = Column(String)  # JSON string para guardar elecciones temporales (ej. {"service_id": 1})
    last_message_at = Column(DateTime, default=datetime.utcnow)