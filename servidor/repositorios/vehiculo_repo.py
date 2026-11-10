from sqlalchemy.orm import Session
from servidor.modelos import Vehiculo, Imagen


class VehiculoRepo:
    def __init__(self, sesion: Session):
        self.sesion = sesion

    def obtener_por_id(self, vehiculo_id: int) -> Vehiculo | None:
        return self.sesion.get(Vehiculo, vehiculo_id)

    def listar(
        self,
        texto: str | None = None,
        marca: str | None = None,
        precio_min: float | None = None,
        precio_max: float | None = None,
        anio_min: int | None = None,
        anio_max: int | None = None,
        km_max: int | None = None,
        color: str | None = None,
        ciudad: str | None = None,
        solo_disponibles: bool = False,
        orden: str = "recientes",
    ) -> list[Vehiculo]:
        consulta = self.sesion.query(Vehiculo).filter(Vehiculo.estado != "Vendido")
        if solo_disponibles:
            consulta = consulta.filter(Vehiculo.estado == "Disponible")

        if texto:
            patron = f"%{texto}%"
            consulta = consulta.filter(
                Vehiculo.marca.ilike(patron) | Vehiculo.modelo.ilike(patron)
            )
        if marca:
            consulta = consulta.filter(Vehiculo.marca.ilike(marca))
        if precio_min is not None:
            consulta = consulta.filter(Vehiculo.precio >= precio_min)
        if precio_max is not None:
            consulta = consulta.filter(Vehiculo.precio <= precio_max)
        if anio_min is not None:
            consulta = consulta.filter(Vehiculo.anio >= anio_min)
        if anio_max is not None:
            consulta = consulta.filter(Vehiculo.anio <= anio_max)
        if km_max is not None:
            consulta = consulta.filter(Vehiculo.kilometraje <= km_max)
        if color:
            consulta = consulta.filter(Vehiculo.color.ilike(f"%{color}%"))
        if ciudad:
            consulta = consulta.filter(Vehiculo.ciudad.ilike(f"%{ciudad}%"))

        orden_sql = {
            "precio_asc": Vehiculo.precio.asc(),
            "precio_desc": Vehiculo.precio.desc(),
            "anio_desc": Vehiculo.anio.desc(),
            "km_asc": Vehiculo.kilometraje.asc(),
            "recientes": Vehiculo.creado_en.desc(),
        }.get(orden, Vehiculo.creado_en.desc())

        return consulta.order_by(orden_sql).all()

    def marcas_disponibles(self) -> list[str]:
        """Marcas de los vehiculos en venta, sin repetir (sin importar mayusculas)."""
        filas = (
            self.sesion.query(Vehiculo.marca)
            .filter(Vehiculo.estado != "Vendido")
            .distinct()
            .all()
        )
        unicas: dict[str, str] = {}
        for (nombre,) in filas:
            nombre = nombre.strip()
            actual = unicas.get(nombre.lower())
            # Si hay "nissan" y "Nissan", se muestra la que tiene mayuscula
            if actual is None or (actual.islower() and not nombre.islower()):
                unicas[nombre.lower()] = nombre
        return sorted(unicas.values(), key=str.lower)

    def listar_por_vendedor(self, vendedor_id: int) -> list[Vehiculo]:
        return (
            self.sesion.query(Vehiculo)
            .filter(Vehiculo.vendedor_id == vendedor_id)
            .order_by(Vehiculo.creado_en.desc())
            .all()
        )

    def crear(self, vehiculo: Vehiculo) -> Vehiculo:
        self.sesion.add(vehiculo)
        self.sesion.commit()
        self.sesion.refresh(vehiculo)
        return vehiculo

    def guardar(self, vehiculo: Vehiculo) -> Vehiculo:
        self.sesion.commit()
        self.sesion.refresh(vehiculo)
        return vehiculo

    def eliminar(self, vehiculo: Vehiculo) -> None:
        self.sesion.delete(vehiculo)
        self.sesion.commit()

    def agregar_imagen(self, imagen: Imagen) -> Imagen:
        self.sesion.add(imagen)
        self.sesion.commit()
        self.sesion.refresh(imagen)
        return imagen