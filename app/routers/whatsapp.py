from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import Response  # Nueva importación para header XML
from sqlalchemy.orm import Session
from twilio.twiml.messaging_response import MessagingResponse
from ..database import get_db
from ..models import Service, Conversation
import os
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

load_dotenv()
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")

router = APIRouter(prefix="/whatsapp", tags=["whatsapp"])

@router.post("/incoming")
async def whatsapp_incoming(request: Request, db: Session = Depends(get_db)):
    logger.info("Webhook llamado - Solicitud recibida")
    form = await request.form()
    logger.info(f"Form data: {dict(form)}")
    from_number = form.get("From")
    message = form.get("Body")
    logger.info(f"From: {from_number}, Body: {message}")

    if not from_number or not message:
        logger.error("Invalid request - Faltan From o Body")
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
        # Template dinámico: Lista servicios de DB (basado en tu PDF)
        services = db.query(Service).all()
        service_list = "\n".join([f"- {s.name}" for s in services])
        reply = f"Hola! Bienvenido a Spa Splendeur. Elige un servicio:\n{service_list}\nResponde con el nombre del servicio."
        response.message(reply)
        conv.state = "choose_service"  # Avanza estado
        db.commit()
    else:
        # Placeholder para próximos estados
        response.message("Mensaje recibido: " + message)

    # Devuelve Response con Content-Type XML para Twilio
    xml_content = str(response)
    logger.info(f"Respuesta XML enviada: {xml_content[:100]}...")  # Log parcial para debug
    return Response(content=xml_content, media_type="text/xml")