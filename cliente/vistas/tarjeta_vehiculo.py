import io

import customtkinter as ctk
from PIL import Image

from cliente.estilos import COLOR_TARJETA, COLOR_TEXTO_CLARO, COLOR_NARANJA, FUENTE

COLOR_BORDE_TARJETA = "#9AA8BF"
_cache_imagenes: dict[str, ctk.CTkImage] = {}


class TarjetaVehiculo(ctk.CTkFrame):
    """Tarjeta del listado: foto, marca, modelo, anio y precio."""

    def __init__(self, padre, api, vehiculo: dict, al_hacer_clic=None):
        super().__init__(padre, fg_color=COLOR_BORDE_TARJETA, corner_radius=18)
        self.api = api
        self.vehiculo = vehiculo

        interior = ctk.CTkFrame(self, fg_color=COLOR_TARJETA, corner_radius=16)
        interior.pack(fill="x", padx=8, pady=8)

        self.etiqueta_foto = ctk.CTkLabel(interior, text="Sin foto", width=150, height=100,
                                          text_color=COLOR_TEXTO_CLARO, font=(FUENTE, 11))
        self.etiqueta_foto.pack(side="left", padx=12, pady=12)
        self._cargar_foto()

        datos = ctk.CTkFrame(interior, fg_color="transparent")
        datos.pack(side="left", fill="y", pady=12)
        for linea in (
            f"Marca: {vehiculo['marca']}",
            f"Modelo: {vehiculo['modelo']}",
            f"Anio: {vehiculo['anio']}",
        ):
            ctk.CTkLabel(datos, text=linea, text_color=COLOR_TEXTO_CLARO,
                         font=(FUENTE, 14), anchor="w").pack(anchor="w")

        derecha = ctk.CTkFrame(interior, fg_color="transparent")
        derecha.pack(side="right", padx=20, pady=12, anchor="n")
        ctk.CTkLabel(derecha, text=f"Precio: {vehiculo['precio']:,.0f} MXN",
                     text_color=COLOR_TEXTO_CLARO, font=(FUENTE, 16)).pack(anchor="e")
        if vehiculo["estado"] != "Disponible":
            ctk.CTkLabel(derecha, text=vehiculo["estado"].upper(), text_color=COLOR_NARANJA,
                         font=(FUENTE, 13, "bold")).pack(anchor="e", pady=(6, 0))

        if al_hacer_clic:
            self._enlazar_clic(self, lambda e: al_hacer_clic(vehiculo))

    def _cargar_foto(self) -> None:
        imagenes = self.vehiculo.get("imagenes", [])
        if not imagenes:
            return
        principal = next((i for i in imagenes if i["es_principal"]), imagenes[0])
        archivo = principal["archivo"]

        if archivo not in _cache_imagenes:
            contenido = self.api.descargar_imagen(archivo)
            if contenido is None:
                return
            try:
                foto = Image.open(io.BytesIO(contenido)).convert("RGB")
            except OSError:
                return
            foto.thumbnail((300, 200))
            _cache_imagenes[archivo] = ctk.CTkImage(foto, size=(150, 100))

        self.etiqueta_foto.configure(image=_cache_imagenes[archivo], text="")

    def _enlazar_clic(self, widget, funcion) -> None:
        widget.bind("<Button-1>", funcion, add="+")
        widget.configure(cursor="hand2")
        for hijo in widget.winfo_children():
            self._enlazar_clic(hijo, funcion)