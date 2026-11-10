import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# En desarrollo usa SQLite; en la nube cambiarás esta línea por la URL de PostgreSQL
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'autos.db'}")

# Cambia esto por una cadena larga y aleatoria; nunca la subas a GitHub
SECRET_KEY = os.getenv("SECRET_KEY", "56314331334231435421312351234984341423441448894345641289344413412133")
ALGORITMO = "HS256"
EXPIRACION_TOKEN_MINUTOS = 60 * 24  # 1 día

CARPETA_UPLOADS = BASE_DIR / "uploads"