from servidor.modelos import Usuario
from servidor.repositorios.usuario_repo import UsuarioRepo
from servidor.seguridad import Seguridad
from servidor.esquemas import RegistroEntrada, LoginEntrada, UsuarioEdicion


class ErrorAuth(Exception):
    """Error de autenticacion o registro, con un mensaje para el usuario."""


class AuthServicio:
    def __init__(self, repo: UsuarioRepo):
        self.repo = repo

    def registrar(self, datos: RegistroEntrada) -> tuple[Usuario, str]:
        if self.repo.obtener_por_nombre(datos.nombre_usuario):
            raise ErrorAuth("Ese nombre de usuario ya esta en uso")
        if self.repo.obtener_por_correo(datos.correo):
            raise ErrorAuth("Ese correo ya esta registrado")

        usuario = Usuario(
            nombre_usuario=datos.nombre_usuario,
            correo=datos.correo,
            contrasena_hash=Seguridad.hashear(datos.contrasena),
            ciudad=datos.ciudad,
            telefono=datos.telefono,
        )
        usuario = self.repo.crear(usuario)
        return usuario, Seguridad.crear_token(usuario.id)

    def iniciar_sesion(self, datos: LoginEntrada) -> tuple[Usuario, str]:
        usuario = self.repo.obtener_por_nombre(datos.nombre_usuario)
        if usuario is None or not Seguridad.verificar(datos.contrasena, usuario.contrasena_hash):
            # Mismo mensaje para ambos casos, asi no se revela si el usuario existe
            raise ErrorAuth("Usuario o contrasena incorrectos")
        return usuario, Seguridad.crear_token(usuario.id)

    def editar_perfil(self, usuario: Usuario, datos: UsuarioEdicion) -> Usuario:
        cambios = datos.model_dump(exclude_unset=True)
        actual = cambios.pop("contrasena_actual", None)
        nueva = cambios.pop("contrasena_nueva", None)

        # Nombre y correo son obligatorios: si llegan vacios (null) se ignoran
        for campo in ("nombre_usuario", "correo"):
            if cambios.get(campo) is None:
                cambios.pop(campo, None)

        nombre = cambios.get("nombre_usuario")
        if nombre and nombre != usuario.nombre_usuario and self.repo.obtener_por_nombre(nombre):
            raise ErrorAuth("Ese nombre de usuario ya esta en uso")
        correo = cambios.get("correo")
        if correo and correo != usuario.correo and self.repo.obtener_por_correo(correo):
            raise ErrorAuth("Ese correo ya esta registrado")

        if nueva:
            if not actual or not Seguridad.verificar(actual, usuario.contrasena_hash):
                raise ErrorAuth("La contrasena actual no es correcta")
            usuario.contrasena_hash = Seguridad.hashear(nueva)

        for campo, valor in cambios.items():
            if campo in ("ciudad", "telefono"):
                valor = (valor or "").strip() or None  # vacio se guarda como "sin dato"
            setattr(usuario, campo, valor)
        return self.repo.guardar(usuario)
