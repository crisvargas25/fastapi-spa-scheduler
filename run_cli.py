import httpx
import asyncio

API_URL = "http://127.0.0.1:8000/appointments/"  # Ajusta si cambias puerto

async def send_message(message: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(API_URL, params={"message": message})
        return response.json()

def main():
    print("Simulador de chat: Escribe mensajes como 'Quiero un masaje el viernes a las 15:00'. Sal con 'exit'.")
    while True:
        message = input("Tú: ")
        if message.lower() == "exit":
            break
        try:
            response = asyncio.run(send_message(message))
            print("Sistema:", response)
        except Exception as e:
            print("Error:", str(e))

if __name__ == "__main__":
    main()