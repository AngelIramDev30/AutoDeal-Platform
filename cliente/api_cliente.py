import requests

from cliente.sesion import Sesion

URL_BASE = "http://127.0.0.1:8000"


class ErrorApi(Exception):
    """Error al hablar con el servidor, con un mensaje listo para mostrar."""

    def __init__(self, mensaje: str, codigo: int | None = None):
        super().__init__(mensaje)
        self.codigo = codigo


class ApiCliente:
    def __init__(self, sesion: Sesion, url_base: str = URL_BASE):
        self.sesion = sesion
        self.url_base = url_base

    # ---------- utilidades internas ----------
    def _peticion(self, metodo: str, ruta: str, **kwargs):
        headers = kwargs.pop("headers", {})
        if self.sesion.token:
            headers["Authorization"] = f"Bearer {self.sesion.token}"
        try:
            resp = requests.request(
                metodo, self.url_base + ruta, headers=headers, timeout=15, **kwargs
            )
        except requests.exceptions.RequestException:
            raise ErrorApi("No se pudo conectar con el servidor")

        if resp.status_code >= 400:
            raise ErrorApi(self._extraer_mensaje(resp), resp.status_code)
        if resp.status_code == 204:
            return None
        return resp.json()

    @staticmethod
    def _extraer_mensaje(resp: requests.Response) -> str:
        try:
            detalle = resp.json().get("detail", "Error desconocido")
        except ValueError:
            return f"Error del servidor ({resp.status_code})"
        if isinstance(detalle, list):  # error de validacion (422)
            primero = detalle[0]
            campo = primero.get("loc", ["dato"])[-1]
            return f"Dato invalido en '{campo}': {primero.get('msg', '')}"
        return str(detalle)

    # ---------- autenticacion ----------
    def registrar(self, nombre_usuario, correo, contrasena, ciudad=None, telefono=None) -> dict:
        datos = self._peticion("POST", "/auth/registro", json={
            "nombre_usuario": nombre_usuario,
            "correo": correo,
            "contrasena": contrasena,
            "ciudad": ciudad or None,
            "telefono": telefono or None,
        })
        self.sesion.iniciar(datos["token"], datos["usuario"])
        return datos

    def iniciar_sesion(self, nombre_usuario, contrasena) -> dict:
        datos = self._peticion("POST", "/auth/login", json={
            "nombre_usuario": nombre_usuario,
            "contrasena": contrasena,
        })
        self.sesion.iniciar(datos["token"], datos["usuario"])
        return datos

    def editar_perfil(self, cambios: dict) -> dict:
        """Guarda los cambios del perfil y actualiza los datos de la sesion."""
        usuario = self._peticion("PUT", "/auth/yo", json=cambios)
        self.sesion.usuario = usuario
        return usuario

    # ---------- vehiculos ----------
    def listar_vehiculos(self, **filtros) -> list[dict]:
        params = {k: v for k, v in filtros.items() if v not in (None, "")}
        return self._peticion("GET", "/vehiculos/", params=params)

    def listar_marcas(self) -> list[str]:
        return self._peticion("GET", "/vehiculos/marcas")

    def mis_vehiculos(self) -> list[dict]:
        return self._peticion("GET", "/vehiculos/mios")

    def detalle_vehiculo(self, vehiculo_id: int) -> dict:
        return self._peticion("GET", f"/vehiculos/{vehiculo_id}")

    def contacto_vendedor(self, vehiculo_id: int) -> dict:
        return self._peticion("GET", f"/vehiculos/{vehiculo_id}/contacto")

    def publicar_vehiculo(self, datos: dict) -> dict:
        return self._peticion("POST", "/vehiculos/", json=datos)

    def editar_vehiculo(self, vehiculo_id: int, cambios: dict) -> dict:
        return self._peticion("PUT", f"/vehiculos/{vehiculo_id}", json=cambios)

    def eliminar_vehiculo(self, vehiculo_id: int) -> None:
        self._peticion("DELETE", f"/vehiculos/{vehiculo_id}")

    def comprar_vehiculo(self, vehiculo_id: int) -> dict:
        return self._peticion("POST", f"/vehiculos/{vehiculo_id}/comprar")

    def subir_imagen(self, vehiculo_id: int, ruta_archivo: str) -> dict:
        with open(ruta_archivo, "rb") as f:
            nombre = ruta_archivo.replace("\\", "/").split("/")[-1]
            return self._peticion(
                "POST", f"/vehiculos/{vehiculo_id}/imagenes", files={"archivo": (nombre, f)}
            )

    def descargar_imagen(self, archivo: str) -> bytes | None:
        try:
            resp = requests.get(f"{self.url_base}/uploads/{archivo}", timeout=15)
            return resp.content if resp.status_code == 200 else None
        except requests.exceptions.RequestException:
            return None