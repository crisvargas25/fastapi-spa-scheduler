from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session
from twilio.twiml.messaging_response import MessagingResponse
from ..database import get_db
from ..models import Service, Conversation
import os
from dotenv import load_dotenv
import logging
from datetime import datetime, timedelta

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

    # Flujo con botones
    response = MessagingResponse()
    if conv.state == "start":
        # Lista servicios como botones
        services = db.query(Service).all()
        msg = "Hola! Bienvenido a Spa Splendeur. Elige un servicio:"
        with response.message(msg) as msg:
            for service in services:
                msg.quick_reply(payload=service.id, content=service.name)
        conv.state = "choose_service"
        conv.data = "{}"  # Inicializa data como JSON vacío
        db.commit()
    elif conv.state == "choose_service":
        # Procesa selección de servicio (botón)
        try:
            service_id = int(message)  # Asume que el payload es el ID
            service = db.query(Service).filter_by(id=service_id).first()
            if not service:
                response.message("Servicio no válido. Elige de nuevo.")
                with response.message() as msg:
                    services = db.query(Service).all()
                    for s in services:
                        msg.quick_reply(payload=s.id, content=s.name)
            else:
                conv.data = f'{{"service_id": {service_id}}}'
                conv.state = "choose_date"
                db.commit()
                # Lista días disponibles (próximos 7 días, placeholder)
                response.message(f"Has elegido: {service.name}. Elige una fecha:")
                with response.message() as msg:
                    for i in range(7):
                        date = (datetime.now() + timedelta(days=i)).strftime("%Y-%m-%d")
                        msg.quick_reply(payload=date, content=date)
        except ValueError:
            response.message("Selección inválida. Elige de nuevo.")
            with response.message() as msg:
                services = db.query(Service).all()
                for s in services:
                    msg.quick_reply(payload=s.id, content=s.name)
    else:
        response.message("Estado no manejado. Contacta a soporte.")

    # Devuelve Response con Content-Type XML
    xml_content = str(response)
    logger.info(f"Respuesta XML enviada: {xml_content[:100]}...")
    return Response(content=xml_content, media_type="text/xml")