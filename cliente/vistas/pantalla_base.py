import customtkinter as ctk

from cliente.estilos import COLOR_FONDO


class PantallaBase(ctk.CTkFrame):
    """Clase padre de todas las pantallas."""

    def __init__(self, app, **datos):
        super().__init__(app, fg_color=COLOR_FONDO, corner_radius=0)
        self.app = app
        self.datos = datos  # datos que otra pantalla quiera pasarle (ej. un vehiculo)
        self.construir()

    def construir(self) -> None:
        """Cada pantalla hija crea aqui sus widgets."""

    def al_mostrar(self) -> None:
        """Se llama justo despues de mostrar la pantalla (ej. para cargar datos)."""