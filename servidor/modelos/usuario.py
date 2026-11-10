from datetime import datetime, timezone
from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from servidor.base_datos import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre_usuario: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    correo: Mapped[str] = mapped_column(String(120), unique=True)
    contrasena_hash: Mapped[str] = mapped_column(String(128))
    ciudad: Mapped[str | None] = mapped_column(String(80), default=None)
    telefono: Mapped[str | None] = mapped_column(String(20), default=None)
    creado_en: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )

    vehiculos: Mapped[list["Vehiculo"]] = relationship(
        back_populates="vendedor", cascade="all, delete-orphan"
    )