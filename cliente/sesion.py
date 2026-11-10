class Sesion:
    "Guarda el token y los datos del usuario que inicio sesion"
    def __init__(self):
        self.token: str | None = None
        self.usuario: dict | None = None

    def iniciar(self, token: str, usuario: dict) -> None:
        self.token = token
        self.usuario = usuario

    def cerrar(self) -> None:
        self.token = None
        self.usuario = None

    @property
    def esta_activa(self) -> bool:
        return self.token is not None