import uuid
from pathlib import Path

from servidor.config import CARPETA_UPLOADS
from servidor.modelos import Usuario, Vehiculo, Imagen
from servidor.repositorios.vehiculo_repo import VehiculoRepo
from servidor.esquemas import VehiculoEntrada, VehiculoEdicion

ESTADOS_VALIDOS = {"Disponible", "Reservado", "Vendido"}
EXTENSIONES_VALIDAS = {".jpg", ".jpeg", ".png", ".webp"}
MAX_IMAGENES = 6
MAX_BYTES_IMAGEN = 5 * 1024 * 1024  # 5 MB


class ErrorVehiculo(Exception):
    """Error de regla de negocio. Lleva un codigo HTTP sugerido."""

    def __init__(self, mensaje: str, codigo: int = 400):
        super().__init__(mensaje)
        self.codigo = codigo


class VehiculoServicio:
    def __init__(self, repo: VehiculoRepo):
        self.repo = repo

    # ---------- consultas ----------
    def obtener(self, vehiculo_id: int) -> Vehiculo:
        vehiculo = self.repo.obtener_por_id(vehiculo_id)
        if vehiculo is None:
            raise ErrorVehiculo("Vehiculo no encontrado", 404)
        return vehiculo

    # ---------- reglas de propiedad ----------
    def _obtener_propio(self, vehiculo_id: int, usuario: Usuario) -> Vehiculo:
        vehiculo = self.obtener(vehiculo_id)
        if vehiculo.vendedor_id != usuario.id:
            raise ErrorVehiculo("No puedes modificar un vehiculo que no es tuyo", 403)
        return vehiculo

    # ---------- acciones ----------
    def publicar(self, datos: VehiculoEntrada, usuario: Usuario) -> Vehiculo:
        vehiculo = Vehiculo(
            vendedor_id=usuario.id,
            marca=datos.marca,
            modelo=datos.modelo,
            anio=datos.anio,
            color=datos.color,
            kilometraje=datos.kilometraje,
            precio=datos.precio,
            descripcion=datos.descripcion,
            ciudad=datos.ciudad or usuario.ciudad,
        )
        return self.repo.crear(vehiculo)

    def editar(self, vehiculo_id: int, datos: VehiculoEdicion, usuario: Usuario) -> Vehiculo:
        vehiculo = self._obtener_propio(vehiculo_id, usuario)
        cambios = datos.model_dump(exclude_unset=True)

        if "estado" in cambios and cambios["estado"] not in ESTADOS_VALIDOS:
            raise ErrorVehiculo(f"Estado invalido. Usa: {', '.join(sorted(ESTADOS_VALIDOS))}")

        for campo, valor in cambios.items():
            setattr(vehiculo, campo, valor)
        return self.repo.guardar(vehiculo)

    def eliminar(self, vehiculo_id: int, usuario: Usuario) -> None:
        vehiculo = self._obtener_propio(vehiculo_id, usuario)
        archivos = [img.archivo for img in vehiculo.imagenes]
        self.repo.eliminar(vehiculo)
        for archivo in archivos:
            (CARPETA_UPLOADS / archivo).unlink(missing_ok=True)

    def comprar(self, vehiculo_id: int, usuario: Usuario) -> Vehiculo:
        """No hay pagos reales: solo marca el auto como Reservado."""
        vehiculo = self.obtener(vehiculo_id)
        if vehiculo.vendedor_id == usuario.id:
            raise ErrorVehiculo("No puedes comprar tu propio vehiculo", 400)
        if vehiculo.estado != "Disponible":
            raise ErrorVehiculo(f"El vehiculo esta {vehiculo.estado.lower()}", 400)
        vehiculo.estado = "Reservado"
        return self.repo.guardar(vehiculo)

    def agregar_imagen(
        self, vehiculo_id: int, usuario: Usuario, nombre_original: str, contenido: bytes
    ) -> Imagen:
        vehiculo = self._obtener_propio(vehiculo_id, usuario)

        extension = Path(nombre_original).suffix.lower()
        if extension not in EXTENSIONES_VALIDAS:
            raise ErrorVehiculo("Formato no permitido. Usa JPG, PNG o WEBP")
        if len(contenido) > MAX_BYTES_IMAGEN:
            raise ErrorVehiculo("La imagen pesa mas de 5 MB")
        if len(vehiculo.imagenes) >= MAX_IMAGENES:
            raise ErrorVehiculo(f"Maximo {MAX_IMAGENES} imagenes por vehiculo")

        # Nombre aleatorio: evita choques y nombres maliciosos del usuario
        nombre_guardado = f"{uuid.uuid4().hex}{extension}"
        CARPETA_UPLOADS.mkdir(parents=True, exist_ok=True)
        (CARPETA_UPLOADS / nombre_guardado).write_bytes(contenido)

        imagen = Imagen(
            vehiculo_id=vehiculo.id,
            archivo=nombre_guardado,
            es_principal=len(vehiculo.imagenes) == 0,  # la primera es la principal
        )
        return self.repo.agregar_imagen(imagen)