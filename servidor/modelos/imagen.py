from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from servidor.base_datos import Base


class Imagen(Base):
    __tablename__ = "imagenes"

    id: Mapped[int] = mapped_column(primary_key=True)
    vehiculo_id: Mapped[int] = mapped_column(ForeignKey("vehiculos.id"), index=True)
    archivo: Mapped[str] = mapped_column(String(200))  # nombre del archivo en uploads/
    es_principal: Mapped[bool] = mapped_column(default=False)

    vehiculo: Mapped["Vehiculo"] = relationship(back_populates="imagenes")