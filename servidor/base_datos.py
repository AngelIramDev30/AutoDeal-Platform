from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from servidor.config import DATABASE_URL

# check_same_thread solo aplica a SQLite
argumentos = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=argumentos)
SesionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    """Clase padre de todos los modelos."""


def obtener_sesion():
    """Dependencia de FastAPI: abre una sesion por peticion y la cierra al terminar."""
    sesion = SesionLocal()
    try:
        yield sesion
    finally:
        sesion.close()