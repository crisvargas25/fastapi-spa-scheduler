import httpx
import os
from dotenv import load_dotenv
from datetime import datetime
import json
import logging
import re

# Configura logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"  # Actualizado a tu modelo

async def process_message_with_ai(message: str) -> dict:
    # Prompt mejorado para formato de fecha completo
    prompt = f"""
    Analiza este mensaje de un cliente para agendar una cita en un spa: "{message}"
    Extrae:
    - client_name: Si no se menciona, usa "Anónimo".
    - service: Si no se especifica, usa "general". Ejemplos: "masaje", "facial".
    - date_time: Formato ISO completo (YYYY-MM-DDTHH:MM:SS). Si es relativo (ej. "mañana"), asume hoy es {datetime.now().date()} y calcula. Si no hay fecha/hora, usa el próximo slot disponible (ej. mañana a las 09:00:00).
    Si falta información o el mensaje es inválido, responde con un JSON que incluya solo la clave "error" con un mensaje descriptivo.
    Responde SOLO con JSON puro, sin texto adicional, sin bloques Markdown (```), sin comentarios ni espacios fuera del JSON.
    Ejemplo de éxito: {{"client_name": "Anónimo", "service": "masaje", "date_time": "2025-09-19T16:00:00"}}
    Ejemplo de error: {{"error": "Información insuficiente para agendar la cita"}}
    """

    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{GEMINI_API_URL}?key={GEMINI_API_KEY}",
                headers=headers,
                json=data
            )
            response.raise_for_status()
            api_response = response.json()
            
            # Loggea la respuesta cruda
            logger.info(f"Respuesta de Gemini: {api_response}")
            
            # Extrae el texto de la respuesta
            try:
                content = api_response["candidates"][0]["content"]["parts"][0]["text"]
                # Limpia Markdown (elimina ```json\n y \n```)
                content = re.sub(r'^```json\n|\n```$', '', content).strip()
                logger.info(f"Contenido limpio: {content}")
                
                # Parsea el JSON
                result = json.loads(content)
                # Valida que el JSON tenga las claves esperadas o error
                if "error" not in result and not all(key in result for key in ["client_name", "service", "date_time"]):
                    return {"error": "Respuesta de Gemini no contiene todas las claves requeridas"}
                return result
            except (KeyError, json.JSONDecodeError) as e:
                logger.error(f"Error al parsear respuesta de Gemini: {str(e)}")
                return {"error": "Respuesta de Gemini no válida o no en formato JSON"}
        except httpx.HTTPStatusError as e:
            logger.error(f"Error en la llamada a Gemini API: {str(e)}")
            return {"error": f"Error en la llamada a Gemini API: {str(e)}"}