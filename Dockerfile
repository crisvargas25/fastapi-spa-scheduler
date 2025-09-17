# Usa una imagen base ligera de Python (elige la versión que uses, ej. 3.11-slim)
FROM python:3.11-slim

# Establece el directorio de trabajo
WORKDIR /app

# Copia requirements.txt primero (para caching de capas en builds futuros)
COPY requirements.txt .

# Instala dependencias (incluye uvicorn si no está en requirements.txt)
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto del código de la app
COPY . .

# Expone el puerto (opcional, pero buena práctica; usa $PORT para que Docker lo resuelva en runtime)
EXPOSE $PORT

# Comando de inicio: Usa la forma exec (array) para que Docker pase $PORT correctamente en runtime
# NO uses RUN aquí; CMD se ejecuta al iniciar el contenedor
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "$PORT"]