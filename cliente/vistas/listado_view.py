import customtkinter as ctk

from cliente.api_cliente import ErrorApi
from cliente.estilos import COLOR_FONDO, COLOR_TEXTO_OSCURO, FUENTE
from cliente.vistas.pantalla_con_header import PantallaConHeader
from cliente.vistas.tarjeta_vehiculo import TarjetaVehiculo


class ListadoView(PantallaConHeader):
    def construir_contenido(self) -> None:
        self.lista = ctk.CTkScrollableFrame(self.contenido, fg_color=COLOR_FONDO)
        self.lista.pack(fill="both", expand=True, padx=30, pady=15)

    def al_mostrar(self) -> None:
        # Filtros que otra pantalla pudo pasar (texto del buscador, o los de "Filtros")
        filtros = dict(self.datos)
        texto = filtros.get("texto", "")
        if texto:
            self.campo_busqueda.insert(0, texto)
        self.cargar(filtros)

    def cargar(self, filtros: dict) -> None:
        for hijo in self.lista.winfo_children():
            hijo.destroy()

        try:
            vehiculos = self.app.api.listar_vehiculos(**filtros)
        except ErrorApi as e:
            ctk.CTkLabel(self.lista, text=str(e), text_color="#B00020",
                         font=(FUENTE, 15)).pack(pady=40)
            return

        if not vehiculos:
            ctk.CTkLabel(self.lista, text="No se encontraron vehiculos",
                         text_color=COLOR_TEXTO_OSCURO, font=(FUENTE, 16)).pack(pady=40)
            return

        for vehiculo in vehiculos:
            TarjetaVehiculo(
                self.lista, self.app.api, vehiculo, al_hacer_clic=self.abrir_detalle
            ).pack(fill="x", pady=8)

    def abrir_detalle(self, vehiculo: dict) -> None:
        self.app.ir_a("detalle", vehiculo_id=vehiculo["id"])