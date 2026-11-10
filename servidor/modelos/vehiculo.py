from datetime import datetime, timezone
from sqlalchemy import String, Text, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from servidor.base_datos import Base


class Vehiculo(Base):
    __tablename__ = "vehiculos"

    id: Mapped[int] = mapped_column(primary_key=True)
    vendedor_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), index=True)
    marca: Mapped[str] = mapped_column(String(50), index=True)
    modelo: Mapped[str] = mapped_column(String(80))
    anio: Mapped[int] = mapped_column()
    color: Mapped[str] = mapped_column(String(30))
    kilometraje: Mapped[int] = mapped_column()
    precio: Mapped[float] = mapped_column()
    descripcion: Mapped[str] = mapped_column(Text, default="")
    ciudad: Mapped[str | None] = mapped_column(String(80), default=None)
    estado: Mapped[str] = mapped_column(String(20), default="Disponible")  # Disponible / Reservado / Vendido
    creado_en: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )

    vendedor: Mapped["Usuario"] = relationship(back_populates="vehiculos")
    imagenes: Mapped[list["Imagen"]] = relationship(
        back_populates="vehiculo", cascade="all, delete-orphan"
    )