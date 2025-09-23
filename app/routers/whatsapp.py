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

def build_quick_replies(items):
    """Construye tags <QuickReply> a partir de una lista de dicts {payload, title}"""
    quick_replies_xml = ""
    for item in items:
        quick_replies_xml += f'<QuickReply payload="{item["payload"]}">{item["title"]}</QuickReply>'
    return quick_replies_xml

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
    response = MessagingResponse()from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session
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

def build_quick_replies(items):
    """Construye tags <QuickReply> a partir de una lista de dicts {payload, title}"""
    return "".join([f'<QuickReply payload="{item["payload"]}">{item["title"]}</QuickReply>' for item in items])

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
    twiml = '<?xml version="1.0" encoding="UTF-8"?><Response>'
    if conv.state == "choose_service":
        services = db.query(Service).all()
        logger.info(f"Servicios encontrados: {services}")
        if not services:
            twiml += "<Message>No hay servicios disponibles. Contacta a soporte.</Message>"
        else:
            quick_replies = [{"payload": str(service.id), "title": service.name} for service in services]
            twiml += f"<Message><Body>Hola! Bienvenido a Spa Splendeur. Elige un servicio:</Body>{build_quick_replies(quick_replies)}</Message>"
            conv.state = "choose_service"
            conv.data = "{}"
            db.commit()
    elif conv.state == "choose_service":
        try:
            service_id = int(message)
            service = db.query(Service).filter_by(id=service_id).first()
            if not service:
                twiml += "<Message><Body>Servicio no válido. Elige de nuevo.</Body>"
                services = db.query(Service).all()
                quick_replies = [{"payload": str(s.id), "title": s.name} for s in services]
                twiml += f"{build_quick_replies(quick_replies)}</Message>"
            else:
                conv.data = f'{{"service_id": {service_id}}}'
                conv.state = "choose_date"
                db.commit()
                twiml += f"<Message><Body>Has elegido: {service.name}. Elige una fecha:</Body>"
                dates = [(datetime.now() + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]
                quick_replies = [{"payload": date, "title": date} for date in dates]
                twiml += f"{build_quick_replies(quick_replies)}</Message>"
        except ValueError:
            twiml += "<Message><Body>Selección inválida. Elige de nuevo.</Body>"
            services = db.query(Service).all()
            quick_replies = [{"payload": str(s.id), "title": s.name} for s in services]
            twiml += f"{build_quick_replies(quick_replies)}</Message>"
    else:
        twiml += "<Message><Body>Estado no manejado. Contacta a soporte.</Body></Message>"

    twiml += "</Response>"
    logger.info(f"Respuesta TwiML enviada: {twiml[:200]}...")
    return Response(content=twiml, media_type="text/xml")
    twiml = '<?xml version="1.0" encoding="UTF-8"?><Response>'
    if conv.state == "choose_service":
        # Lista servicios como botones (quick replies)
        services = db.query(Service).all()
        logger.info(f"Servicios encontrados: {services}")
        if not services:
            twiml += "<Message>No hay servicios disponibles. Contacta a soporte.</Message>"
        else:
            quick_replies = [{"payload": str(service.id), "title": service.name} for service in services]
            twiml += f"<Message><Body>Hola! Bienvenido a Spa Splendeur. Elige un servicio:</Body>{build_quick_replies(quick_replies)}</Message>"
            conv.state = "choose_service"
            conv.data = "{}"  # Inicializa data como JSON vacío
            db.commit()
    elif conv.state == "choose_service":
        # Procesa selección de servicio (botón)
        try:
            service_id = int(message)  # Payload es el ID como string
            service = db.query(Service).filter_by(id=service_id).first()
            if not service:
                twiml += "<Message>Servicio no válido. Elige de nuevo.</Message>"
                services = db.query(Service).all()
                quick_replies = [{"payload": str(s.id), "title": s.name} for s in services]
                twiml += f"<Message><Body>Elige un servicio:</Body>{build_quick_replies(quick_replies)}</Message>"
            else:
                conv.data = f'{{"service_id": {service_id}}}'
                conv.state = "choose_date"
                db.commit()
                # Lista días disponibles (próximos 7 días, placeholder)
                twiml += f"<Message><Body>Has elegido: {service.name}. Elige una fecha:</Body>"
                dates = [(datetime.now() + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]
                quick_replies = [{"payload": date, "title": date} for date in dates]
                twiml += f"{build_quick_replies(quick_replies)}</Message>"
        except ValueError:
            twiml += "<Message>Selección inválida. Elige de nuevo.</Message>"
            services = db.query(Service).all()
            quick_replies = [{"payload": str(s.id), "title": s.name} for s in services]
            twiml += f"<Message><Body>Elige un servicio:</Body>{build_quick_replies(quick_replies)}</Message>"
    else:
        twiml += "<Message>Estado no manejado. Contacta a soporte.</Message>"

    twiml += "</Response>"
    logger.info(f"Respuesta TwiML enviada: {twiml[:200]}...")
    return Response(content=twiml, media_type="text/xml")