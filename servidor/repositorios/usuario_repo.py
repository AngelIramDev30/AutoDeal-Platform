from sqlalchemy.orm import Session
from servidor.modelos import Usuario


class UsuarioRepo:
    def __init__(self, sesion: Session):
        self.sesion = sesion

    def obtener_por_id(self, usuario_id: int) -> Usuario | None:
        return self.sesion.get(Usuario, usuario_id)

    def obtener_por_nombre(self, nombre_usuario: str) -> Usuario | None:
        return self.sesion.query(Usuario).filter(
            Usuario.nombre_usuario == nombre_usuario
        ).first()

    def obtener_por_correo(self, correo: str) -> Usuario | None:
        return self.sesion.query(Usuario).filter(Usuario.correo == correo).first()

    def guardar(self, usuario: Usuario) -> Usuario:
        self.sesion.commit()
        self.sesion.refresh(usuario)
        return usuario

    def crear(self, usuario: Usuario) -> Usuario:
        self.sesion.add(usuario)
        self.sesion.commit()
        self.sesion.refresh(usuario)
        return usuario