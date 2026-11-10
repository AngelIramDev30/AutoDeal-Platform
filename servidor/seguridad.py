from datetime import datetime, timedelta, timezone
import bcrypt
import jwt
from servidor.config import SECRET_KEY, ALGORITMO, EXPIRACION_TOKEN_MINUTOS


class Seguridad:
    """Agrupa todo lo relacionado con contraseñas y tokens."""

    @staticmethod
    def hashear(contrasena: str) -> str:
        return bcrypt.hashpw(contrasena.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    @staticmethod
    def verificar(contrasena: str, hash_guardado: str) -> bool:
        return bcrypt.checkpw(contrasena.encode("utf-8"), hash_guardado.encode("utf-8"))

    @staticmethod
    def crear_token(usuario_id: int) -> str:
        expira = datetime.now(timezone.utc) + timedelta(minutes=EXPIRACION_TOKEN_MINUTOS)
        datos = {"sub": str(usuario_id), "exp": expira}
        return jwt.encode(datos, SECRET_KEY, algorithm=ALGORITMO)

    @staticmethod
    def leer_token(token: str) -> int | None:
        """Devuelve el id del usuario, o None si el token es inválido o expiró."""
        try:
            datos = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITMO])
            return int(datos["sub"])
        except (jwt.PyJWTError, KeyError, ValueError):
            return None