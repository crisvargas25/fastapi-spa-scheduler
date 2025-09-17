# Usa una imagen base ligera de Python
FROM python:3.11-slim

# Establece el directorio de trabajo
WORKDIR /app

# Copia requirements.txt primero (para caching)
COPY requirements.txt .

# Instala dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto del código
COPY . .

# Expone el puerto (fijo, ya que $PORT no se resuelve en build time)
EXPOSE 8080

# Usa forma shell para que $PORT se expanda en runtime
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}