from tkinter import messagebox

import customtkinter as ctk

from cliente.api_cliente import ErrorApi
from cliente.estilos import (
    COLOR_FONDO, COLOR_VERDE, COLOR_NARANJA, COLOR_TARJETA,
    COLOR_TEXTO_CLARO, COLOR_TEXTO_OSCURO, FUENTE,
)
from cliente.vistas.pantalla_con_header import PantallaConHeader
from cliente.vistas.tarjeta_vehiculo import TarjetaVehiculo

COLOR_ROJO = "#C0504D"


class MisPublicacionesView(PantallaConHeader):
    """Lista los vehiculos del usuario con botones para editar, marcar vendido y eliminar."""

    def construir_contenido(self) -> None:
        encabezado = ctk.CTkFrame(self.contenido, fg_color="transparent")
        encabezado.pack(fill="x", padx=30, pady=(10, 0))
        self.crear_boton_volver(encabezado).pack(side="left")
        ctk.CTkLabel(encabezado, text="Mis publicaciones", text_color=COLOR_TEXTO_OSCURO,
                     font=(FUENTE, 22, "bold")).pack(side="left", padx=20)

        self.lista = ctk.CTkScrollableFrame(self.contenido, fg_color=COLOR_FONDO)
        self.lista.pack(fill="both", expand=True, padx=30, pady=(5, 15))

    def al_mostrar(self) -> None:
        self.cargar()

    # ---------- carga ----------
    def cargar(self) -> None:
        for hijo in self.lista.winfo_children():
            hijo.destroy()

        try:
            vehiculos = self.app.api.mis_vehiculos()
        except ErrorApi as e:
            ctk.CTkLabel(self.lista, text=str(e), text_color="#B00020",
                         font=(FUENTE, 15)).pack(pady=40)
            return

        if not vehiculos:
            ctk.CTkLabel(self.lista, text="Aun no has publicado ningun vehiculo",
                         text_color=COLOR_TEXTO_OSCURO, font=(FUENTE, 16)).pack(pady=(40, 12))
            ctk.CTkButton(
                self.lista, text="Publicar mi primer vehiculo", width=220, height=36,
                corner_radius=18, fg_color=COLOR_NARANJA, hover_color="#D4763F",
                text_color=COLOR_TEXTO_OSCURO, font=(FUENTE, 14, "bold"),
                command=lambda: self.app.ir_a("publicar"),
            ).pack()
            return

        for vehiculo in vehiculos:
            self._crear_fila(vehiculo)

    def _crear_fila(self, v: dict) -> None:
        fila = ctk.CTkFrame(self.lista, fg_color="transparent")
        fila.pack(fill="x", pady=(8, 4))

        TarjetaVehiculo(fila, self.app.api, v, al_hacer_clic=self.abrir_detalle).pack(fill="x")

        botones = ctk.CTkFrame(fila, fg_color="transparent")
        botones.pack(anchor="e", pady=(6, 0), padx=8)

        estado = v["estado"]
        if estado != "Vendido":
            self._boton(botones, "Marcar como vendido", COLOR_VERDE, 170,
                        lambda: self.cambiar_estado(v, "Vendido"))
        if estado == "Reservado":
            self._boton(botones, "Liberar", COLOR_TARJETA, 90,
                        lambda: self.cambiar_estado(v, "Disponible"))
        if estado == "Vendido":
            self._boton(botones, "Volver a publicar", COLOR_TARJETA, 150,
                        lambda: self.cambiar_estado(v, "Disponible"))
        self._boton(botones, "Editar", COLOR_NARANJA, 90,
                    lambda: self.app.ir_a("editar", vehiculo_id=v["id"]))
        self._boton(botones, "Eliminar", COLOR_ROJO, 90, lambda: self.eliminar(v))

    @staticmethod
    def _boton(padre, texto: str, color: str, ancho: int, comando) -> None:
        ctk.CTkButton(
            padre, text=texto, width=ancho, height=30, corner_radius=15, fg_color=color,
            hover_color=color, text_color=COLOR_TEXTO_CLARO, font=(FUENTE, 12, "bold"),
            command=comando,
        ).pack(side="left", padx=4)

    # ---------- acciones ----------
    def abrir_detalle(self, vehiculo: dict) -> None:
        self.app.ir_a("detalle", vehiculo_id=vehiculo["id"])

    def cambiar_estado(self, v: dict, nuevo: str) -> None:
        nombre = f"{v['marca']} {v['modelo']}"
        mensajes = {
            "Vendido": f"Marcar el {nombre} como vendido?\nYa no aparecera en el listado.",
            "Disponible": f"Poner el {nombre} como disponible?\nVolvera a aparecer en el listado.",
        }
        if not messagebox.askyesno("Confirmar", mensajes[nuevo]):
            return
        try:
            self.app.api.editar_vehiculo(v["id"], {"estado": nuevo})
        except ErrorApi as e:
            messagebox.showerror("No se pudo cambiar el estado", str(e))
            return
        self.cargar()

    def eliminar(self, v: dict) -> None:
        nombre = f"{v['marca']} {v['modelo']}"
        if not messagebox.askyesno(
            "Eliminar publicacion",
            f"Eliminar el {nombre}?\nSe borraran tambien sus fotos y no se puede deshacer.",
        ):
            return
        try:
            self.app.api.eliminar_vehiculo(v["id"])
        except ErrorApi as e:
            messagebox.showerror("No se pudo eliminar", str(e))
            return
        self.cargar()
