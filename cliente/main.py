import customtkinter as ctk

from cliente.api_cliente import ApiCliente
from cliente.sesion import Sesion
from cliente.vistas.login_view import LoginView
from cliente.vistas.registro_view import RegistroView
from cliente.vistas.listado_view import ListadoView
from cliente.vistas.publicar_view import PublicarView
from cliente.vistas.detalle_view import DetalleView
from cliente.vistas.filtros_view import FiltrosView
from cliente.vistas.mis_publicaciones_view import MisPublicacionesView
from cliente.vistas.editar_view import EditarView
from cliente.vistas.perfil_view import PerfilView


class App(ctk.CTk):
    PANTALLAS = {
        "login": LoginView,
        "registro": RegistroView,
        "listado": ListadoView,
        "publicar": PublicarView,
        "detalle": DetalleView,
        "filtros": FiltrosView,
        "mis_publicaciones": MisPublicacionesView,
        "editar": EditarView,
        "perfil": PerfilView,
    }

    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("light")
        self.title("Autos App")
        self.geometry("1100x700")
        self.minsize(900, 700)

        self.sesion = Sesion()
        self.api = ApiCliente(self.sesion)
        self.pantalla_actual = None
        self.nombre_actual: str | None = None
        self.datos_actual: dict = {}
        self.anterior: tuple[str, dict] | None = None  # pantalla a la que vuelve "Volver"

        self.ir_a("login")

    def ir_a(self, nombre: str, **datos) -> None:
        if nombre not in self.PANTALLAS:
            print(f"Pantalla '{nombre}' aun no esta disponible")
            return
        if self.pantalla_actual is not None:
            # Se recuerda la pantalla que se deja (con sus datos, ej. filtros) para poder volver.
            # Login y registro no cuentan: no se debe volver a ellos con la sesion iniciada.
            if self.nombre_actual in ("login", "registro"):
                self.anterior = None
            else:
                self.anterior = (self.nombre_actual, self.datos_actual)
            self.pantalla_actual.destroy()
        self.nombre_actual = nombre
        self.datos_actual = datos
        clase = self.PANTALLAS[nombre]
        self.pantalla_actual = clase(self, **datos)
        self.pantalla_actual.pack(fill="both", expand=True)
        self.pantalla_actual.al_mostrar()

    def volver(self) -> None:
        """Regresa a la pantalla anterior (o al listado si no hay ninguna)."""
        if self.anterior and self.anterior[0] != self.nombre_actual:
            nombre, datos = self.anterior
            self.ir_a(nombre, **datos)
        else:
            self.ir_a("listado")

    def cerrar_sesion(self) -> None:
        self.sesion.cerrar()
        self.ir_a("login")


if __name__ == "__main__":
    App().mainloop()