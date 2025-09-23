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
    form_data = dict(form)
    logger.info(f"Form data: {form_data}")
    from_number = form_data.get("From")
    message = form_data.get("Body")
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
        # Lista servicios como botones (quick replies)
        services = db.query(Service).all()
        logger.info(f"Servicios encontrados: {services}")  # Debug
        if not services:
            response.message("No hay servicios disponibles. Contacta a soporte.")
        else:
            quick_replies = [{"payload": str(service.id), "title": service.name} for service in services]
            response.message(
                "Hola! Bienvenido a Spa Splendeur. Elige un servicio:",
                quick_replies=quick_replies
            )
            conv.state = "choose_service"
            conv.data = "{}"  # Inicializa data como JSON vacío
            db.commit()
    elif conv.state == "choose_service":
        # Procesa selección de servicio (botón)
        try:
            service_id = int(message)  # Payload es el ID como string
            service = db.query(Service).filter_by(id=service_id).first()
            if not service:
                response.message("Servicio no válido. Elige de nuevo.")
                services = db.query(Service).all()
                quick_replies = [{"payload": str(s.id), "title": s.name} for s in services]
                response.message("Elige un servicio:", quick_replies=quick_replies)
            else:
                conv.data = f'{{"service_id": {service_id}}}'
                conv.state = "choose_date"
                db.commit()
                # Lista días disponibles (próximos 7 días, placeholder)
                response.message(f"Has elegido: {service.name}. Elige una fecha:")
                dates = [(datetime.now() + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]
                quick_replies = [{"payload": date, "title": date} for date in dates]
                response.message(quick_replies=quick_replies)
        except ValueError:
            response.message("Selección inválida. Elige de nuevo.")
            services = db.query(Service).all()
            quick_replies = [{"payload": str(s.id), "title": s.name} for s in services]
            response.message("Elige un servicio:", quick_replies=quick_replies)
    else:
        response.message("Estado no manejado. Contacta a soporte.")

    # Devuelve Response con Content-Type XML
    xml_content = str(response)
    logger.info(f"Respuesta XML enviada: {xml_content[:100]}...")
    return Response(content=xml_content, media_type="text/xml")