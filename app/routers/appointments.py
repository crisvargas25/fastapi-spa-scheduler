from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, schemas, services
from ..database import get_db
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/appointments", tags=["appointments"])

@router.post("/", response_model=schemas.AppointmentResponse)
async def create_appointment(message: str, db: Session = Depends(get_db)):
    try:
        ai_data = await services.process_message_with_ai(message)
        logger.info(f"Datos de IA: {ai_data}")
        
        # Maneja errores de la IA
        if "error" in ai_data:
            raise HTTPException(status_code=400, detail=ai_data["error"])
            
        # Valida y corrige date_time
        date_time_str = ai_data["date_time"]
        try:
            # Intenta parsear directamente
            date_time = datetime.fromisoformat(date_time_str)
        except ValueError:
            # Si falla (ej. sin segundos), agrega :00 y reintenta
            if len(date_time_str.split(':')) == 2:  # Solo HH:MM
                date_time_str += ":00"
                date_time = datetime.fromisoformat(date_time_str)
            else:
                raise HTTPException(status_code=400, detail="Formato de fecha inválido. Debe ser YYYY-MM-DDTHH:MM:SS")
            
        appointment = models.Appointment(
            client_name=ai_data["client_name"],
            service=ai_data["service"],
            date_time=date_time
        )
        db.add(appointment)
        db.commit()
        db.refresh(appointment)
        logger.info(f"Cita creada: {appointment.id}")
        return appointment
    except HTTPException:
        raise  # Re-lanza excepciones de FastAPI
    except Exception as e:
        logger.error(f"Error al crear cita: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")