from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session

from servidor.base_datos import obtener_sesion
from servidor.esquemas import (
    VehiculoEntrada, VehiculoEdicion, VehiculoSalida, ImagenSalida, ContactoSalida,
)
from servidor.modelos import Usuario
from servidor.repositorios.vehiculo_repo import VehiculoRepo
from servidor.rutas.auth import usuario_actual
from servidor.servicios.vehiculo_servicio import VehiculoServicio, ErrorVehiculo

router = APIRouter(prefix="/vehiculos", tags=["Vehiculos"])


def obtener_servicio(sesion: Session = Depends(obtener_sesion)) -> VehiculoServicio:
    return VehiculoServicio(VehiculoRepo(sesion))


def _error_http(e: ErrorVehiculo) -> HTTPException:
    return HTTPException(e.codigo, str(e))


@router.get("/", response_model=list[VehiculoSalida])
def listar(
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
    servicio: VehiculoServicio = Depends(obtener_servicio),
):
    return servicio.repo.listar(
        texto=texto, marca=marca, precio_min=precio_min, precio_max=precio_max,
        anio_min=anio_min, anio_max=anio_max, km_max=km_max, color=color,
        ciudad=ciudad, solo_disponibles=solo_disponibles, orden=orden,
    )


# IMPORTANTE: /marcas tambien va antes de /{vehiculo_id}
@router.get("/marcas", response_model=list[str])
def marcas(servicio: VehiculoServicio = Depends(obtener_servicio)):
    return servicio.repo.marcas_disponibles()


# IMPORTANTE: /mios va antes de /{vehiculo_id}, si no FastAPI creeria que "mios" es un id
@router.get("/mios", response_model=list[VehiculoSalida])
def mis_vehiculos(
    usuario: Usuario = Depends(usuario_actual),
    servicio: VehiculoServicio = Depends(obtener_servicio),
):
    return servicio.repo.listar_por_vendedor(usuario.id)


@router.get("/{vehiculo_id}", response_model=VehiculoSalida)
def detalle(vehiculo_id: int, servicio: VehiculoServicio = Depends(obtener_servicio)):
    try:
        return servicio.obtener(vehiculo_id)
    except ErrorVehiculo as e:
        raise _error_http(e)


@router.get("/{vehiculo_id}/contacto", response_model=ContactoSalida)
def contacto(
    vehiculo_id: int,
    usuario: Usuario = Depends(usuario_actual),  # solo con sesion iniciada
    servicio: VehiculoServicio = Depends(obtener_servicio),
):
    try:
        return servicio.obtener(vehiculo_id).vendedor
    except ErrorVehiculo as e:
        raise _error_http(e)


@router.post("/", response_model=VehiculoSalida, status_code=status.HTTP_201_CREATED)
def publicar(
    datos: VehiculoEntrada,
    usuario: Usuario = Depends(usuario_actual),
    servicio: VehiculoServicio = Depends(obtener_servicio),
):
    return servicio.publicar(datos, usuario)


@router.put("/{vehiculo_id}", response_model=VehiculoSalida)
def editar(
    vehiculo_id: int,
    datos: VehiculoEdicion,
    usuario: Usuario = Depends(usuario_actual),
    servicio: VehiculoServicio = Depends(obtener_servicio),
):
    try:
        return servicio.editar(vehiculo_id, datos, usuario)
    except ErrorVehiculo as e:
        raise _error_http(e)


@router.delete("/{vehiculo_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar(
    vehiculo_id: int,
    usuario: Usuario = Depends(usuario_actual),
    servicio: VehiculoServicio = Depends(obtener_servicio),
):
    try:
        servicio.eliminar(vehiculo_id, usuario)
    except ErrorVehiculo as e:
        raise _error_http(e)


@router.post("/{vehiculo_id}/comprar", response_model=VehiculoSalida)
def comprar(
    vehiculo_id: int,
    usuario: Usuario = Depends(usuario_actual),
    servicio: VehiculoServicio = Depends(obtener_servicio),
):
    try:
        return servicio.comprar(vehiculo_id, usuario)
    except ErrorVehiculo as e:
        raise _error_http(e)


@router.post("/{vehiculo_id}/imagenes", response_model=ImagenSalida, status_code=status.HTTP_201_CREATED)
async def subir_imagen(
    vehiculo_id: int,
    archivo: UploadFile = File(...),
    usuario: Usuario = Depends(usuario_actual),
    servicio: VehiculoServicio = Depends(obtener_servicio),
):
    contenido = await archivo.read()
    try:
        return servicio.agregar_imagen(vehiculo_id, usuario, archivo.filename or "", contenido)
    except ErrorVehiculo as e:
        raise _error_http(e)