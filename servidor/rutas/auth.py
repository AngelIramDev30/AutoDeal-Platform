from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from servidor.base_datos import obtener_sesion
from servidor.esquemas import (
    RegistroEntrada, LoginEntrada, TokenSalida, UsuarioSalida, UsuarioEdicion,
)
from servidor.modelos import Usuario
from servidor.repositorios.usuario_repo import UsuarioRepo
from servidor.servicios.auth_servicio import AuthServicio, ErrorAuth
from servidor.seguridad import Seguridad

router = APIRouter(prefix="/auth", tags=["Autenticacion"])
esquema_bearer = HTTPBearer()


def usuario_actual(
    credenciales: HTTPAuthorizationCredentials = Depends(esquema_bearer),
    sesion: Session = Depends(obtener_sesion),
) -> Usuario:
    """Lee el token del encabezado y devuelve el usuario. Sirve para proteger rutas."""
    usuario_id = Seguridad.leer_token(credenciales.credentials)
    usuario = UsuarioRepo(sesion).obtener_por_id(usuario_id) if usuario_id else None
    if usuario is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Sesion invalida o expirada")
    return usuario


@router.post("/registro", response_model=TokenSalida, status_code=status.HTTP_201_CREATED)
def registro(datos: RegistroEntrada, sesion: Session = Depends(obtener_sesion)):
    try:
        usuario, token = AuthServicio(UsuarioRepo(sesion)).registrar(datos)
    except ErrorAuth as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(e))
    return TokenSalida(token=token, usuario=UsuarioSalida.model_validate(usuario))


@router.post("/login", response_model=TokenSalida)
def login(datos: LoginEntrada, sesion: Session = Depends(obtener_sesion)):
    try:
        usuario, token = AuthServicio(UsuarioRepo(sesion)).iniciar_sesion(datos)
    except ErrorAuth as e:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, str(e))
    return TokenSalida(token=token, usuario=UsuarioSalida.model_validate(usuario))


@router.get("/yo", response_model=UsuarioSalida)
def yo(usuario: Usuario = Depends(usuario_actual)):
    """Devuelve el usuario dueno del token. Util para probar que la sesion funciona."""
    return usuario


@router.put("/yo", response_model=UsuarioSalida)
def editar_yo(
    datos: UsuarioEdicion,
    usuario: Usuario = Depends(usuario_actual),
    sesion: Session = Depends(obtener_sesion),
):
    """Edita el perfil del usuario que inicio sesion."""
    try:
        return AuthServicio(UsuarioRepo(sesion)).editar_perfil(usuario, datos)
    except ErrorAuth as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(e))
