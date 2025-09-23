from fastapi import APIRouter, Request, Depends, HTTPException
from sqlalchemy.orm import Session
from twilio.twiml.messaging_response import MessagingResponse
from ..database import get_db
from ..models import Service, Conversation  # Importa Service y Conversation
import os
from dotenv import load_dotenv

load_dotenv()
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")

router = APIRouter(prefix="/whatsapp", tags=["whatsapp"])

@router.post("/incoming")
async def whatsapp_incoming(request: Request, db: Session = Depends(get_db)):
    form = await request.form()
    from_number = form.get("From")
    message = form.get("Body")

    if not from_number or not message:
        raise HTTPException(status_code=400, detail="Invalid request")

    # Busca o crea conversación
    conv = db.query(Conversation).filter_by(phone=from_number).first()
    if not conv:
        conv = Conversation(phone=from_number, state="start")
        db.add(conv)
        db.commit()
        db.refresh(conv)

    # Flujo simple inicial: Responde con template de bienvenida
    response = MessagingResponse()
    if conv.state == "start":
        # Template dinámico: Lista servicios de DB
        services = db.query(Service).all()
        service_list = "\n".join([f"- {s.name}" for s in services])
        reply = f"Hola! Bienvenido a Spa Splendeur. Elige un servicio:\n{service_list}\nResponde con el nombre del servicio."
        response.message(reply)
        conv.state = "choose_service"  # Avanza estado
        db.commit()
    else:
        # Placeholder para próximos estados
        response.message("Mensaje recibido: " + message)

    return str(response)