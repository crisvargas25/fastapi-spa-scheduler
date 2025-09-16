from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL, connect_args={"sslmode": "require"})

try:
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        print("Conexión a PostgreSQL exitosa:", result.fetchone())
except Exception as e:
    print("Error al conectar a PostgreSQL:", str(e))