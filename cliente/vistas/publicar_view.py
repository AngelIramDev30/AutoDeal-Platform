from tkinter import filedialog

import customtkinter as ctk
from PIL import Image

from cliente.api_cliente import ErrorApi
from cliente.estilos import (
    COLOR_TARJETA, COLOR_CAMPO, COLOR_NARANJA, COLOR_TEXTO_CLARO,
    COLOR_TEXTO_OSCURO, COLOR_ERROR, FUENTE,
)
from cliente.vistas.pantalla_con_header import PantallaConHeader

MAX_IMAGENES = 6
COLOR_BORDE_TARJETA = "#9AA8BF"
COLOR_CAJA_IMAGEN = "#8697B5"


class PublicarView(PantallaConHeader):
    def construir_contenido(self) -> None:
        self.rutas_imagenes: list[str] = []

        self.crear_boton_volver(self.contenido).pack(anchor="w", padx=30, pady=(10, 0))

        marco = ctk.CTkFrame(self.contenido, fg_color=COLOR_BORDE_TARJETA, corner_radius=18)
        marco.pack(fill="both", expand=True, padx=30, pady=(5, 20))
        tarjeta = ctk.CTkFrame(marco, fg_color=COLOR_TARJETA, corner_radius=16)
        tarjeta.pack(fill="both", expand=True, padx=8, pady=8)
        tarjeta.grid_columnconfigure(1, weight=1)

        # ---- izquierda: imagenes ----
        self.caja_imagen = ctk.CTkButton(
            tarjeta, text="+\nAgregar imagenes", width=240, height=200, corner_radius=14,
            fg_color=COLOR_CAJA_IMAGEN, hover_color="#7787A5", text_color=COLOR_TEXTO_OSCURO,
            font=(FUENTE, 16), command=self.elegir_imagenes,
        )
        self.caja_imagen.grid(row=0, column=0, rowspan=4, padx=20, pady=20, sticky="n")

        self.etiqueta_cantidad = ctk.CTkLabel(
            tarjeta, text=f"0 de {MAX_IMAGENES} imagenes", text_color=COLOR_TEXTO_CLARO,
            font=(FUENTE, 12),
        )
        self.etiqueta_cantidad.grid(row=4, column=0, padx=20, sticky="n")

        ctk.CTkButton(
            tarjeta, text="Quitar imagenes", width=140, height=26, fg_color="transparent",
            hover=False, text_color=COLOR_TEXTO_CLARO, font=(FUENTE, 11, "underline"),
            command=self.quitar_imagenes,
        ).grid(row=5, column=0, padx=20, sticky="n")

        # ---- derecha: campos ----
        formulario = ctk.CTkFrame(tarjeta, fg_color="transparent")
        formulario.grid(row=0, column=1, rowspan=3, sticky="nw", pady=20)

        self.campos = {}
        datos_campos = [
            ("marca", "Marca:"), ("modelo", "Modelo:"), ("anio", "Anio:"),
            ("color", "Color:"), ("kilometraje", "Kilometraje:"),
            ("precio", "Precio (MXN):"), ("ciudad", "Ciudad:"),
        ]
        for fila, (clave, titulo) in enumerate(datos_campos):
            ctk.CTkLabel(formulario, text=titulo, text_color=COLOR_TEXTO_CLARO,
                         font=(FUENTE, 13)).grid(row=fila, column=0, sticky="e", padx=(0, 8), pady=3)
            campo = ctk.CTkEntry(
                formulario, width=240, height=30, corner_radius=10, fg_color=COLOR_CAMPO,
                text_color=COLOR_TEXTO_OSCURO, border_color="black", border_width=2,
            )
            campo.grid(row=fila, column=1, pady=3, sticky="w")
            self.campos[clave] = campo

        ciudad_usuario = self.app.sesion.usuario.get("ciudad")
        if ciudad_usuario:
            self.campos["ciudad"].insert(0, ciudad_usuario)

        # ---- descripcion ----
        ctk.CTkLabel(tarjeta, text="Descripcion:", text_color=COLOR_TEXTO_CLARO,
                     font=(FUENTE, 13)).grid(row=6, column=0, columnspan=2, sticky="w", padx=20)
        self.texto_descripcion = ctk.CTkTextbox(
            tarjeta, height=90, corner_radius=10, fg_color=COLOR_CAMPO,
            text_color=COLOR_TEXTO_OSCURO, border_color="black", border_width=2,
        )
        self.texto_descripcion.grid(row=7, column=0, columnspan=2, sticky="ew", padx=20, pady=(2, 8))

        # ---- pie: error y boton ----
        self.etiqueta_error = ctk.CTkLabel(
            tarjeta, text="", text_color=COLOR_ERROR, font=(FUENTE, 12), wraplength=500,
        )
        self.etiqueta_error.grid(row=8, column=0, columnspan=2, sticky="w", padx=20)

        self.boton_publicar = ctk.CTkButton(
            tarjeta, text="Publicar", width=150, height=38, corner_radius=19,
            fg_color=COLOR_NARANJA, hover_color="#D4763F", text_color=COLOR_TEXTO_OSCURO,
            font=(FUENTE, 15, "bold"), command=self.publicar,
        )
        self.boton_publicar.grid(row=9, column=1, sticky="e", padx=20, pady=(4, 14))

    # ---------- imagenes ----------
    def elegir_imagenes(self) -> None:
        rutas = filedialog.askopenfilenames(
            title="Elige las fotos del vehiculo",
            filetypes=[("Imagenes", "*.jpg *.jpeg *.png *.webp")],
        )
        if not rutas:
            return
        disponibles = MAX_IMAGENES - len(self.rutas_imagenes)
        self.rutas_imagenes.extend(rutas[:disponibles])
        if len(rutas) > disponibles:
            self.etiqueta_error.configure(text=f"Solo se admiten {MAX_IMAGENES} imagenes")
        self._actualizar_vista_imagenes()

    def quitar_imagenes(self) -> None:
        self.rutas_imagenes.clear()
        self._actualizar_vista_imagenes()

    def _actualizar_vista_imagenes(self) -> None:
        self.etiqueta_cantidad.configure(
            text=f"{len(self.rutas_imagenes)} de {MAX_IMAGENES} imagenes"
        )
        if not self.rutas_imagenes:
            self.caja_imagen.configure(image=None, text="+\nAgregar imagenes")
            return
        try:
            foto = Image.open(self.rutas_imagenes[0]).convert("RGB")
            foto.thumbnail((480, 400))
            miniatura = ctk.CTkImage(foto, size=(240, 200))
            self.caja_imagen.configure(image=miniatura, text="")
        except OSError:
            self.caja_imagen.configure(image=None, text="No se pudo mostrar\nla imagen")

    # publicar
    def _leer_datos(self) -> dict | None:
        """Valida el formulario. Devuelve el diccionario o None si hay un error."""
        c = {k: v.get().strip() for k, v in self.campos.items()}

        if len(c["marca"]) < 2:
            return self._error("Escribe la marca")
        if not c["modelo"]:
            return self._error("Escribe el modelo")
        if not c["color"] or len(c["color"]) < 2:
            return self._error("Escribe el color")
        try:
            anio = int(c["anio"])
            kilometraje = int(c["kilometraje"].replace(",", ""))
            precio = float(c["precio"].replace(",", ""))
        except ValueError:
            return self._error("Anio, kilometraje y precio deben ser numeros")
        if not 1900 <= anio <= 2100:
            return self._error("El anio no es valido")
        if kilometraje < 0:
            return self._error("El kilometraje no puede ser negativo")
        if precio <= 0:
            return self._error("El precio debe ser mayor a 0")

        return {
            "marca": c["marca"], "modelo": c["modelo"], "anio": anio, "color": c["color"],
            "kilometraje": kilometraje, "precio": precio, "ciudad": c["ciudad"] or None,
            "descripcion": self.texto_descripcion.get("1.0", "end").strip(),
        }

    def _error(self, mensaje: str) -> None:
        self.etiqueta_error.configure(text=mensaje)
        return None

    def publicar(self) -> None:
        self.etiqueta_error.configure(text="")
        datos = self._leer_datos()
        if datos is None:
            return

        self.boton_publicar.configure(state="disabled", text="Publicando...")
        self.update_idletasks()
        try:
            vehiculo = self.app.api.publicar_vehiculo(datos)
        except ErrorApi as e:
            self.etiqueta_error.configure(text=str(e))
            self.boton_publicar.configure(state="normal", text="Publicar")
            return

        fallidas = 0
        for ruta in self.rutas_imagenes:
            try:
                self.app.api.subir_imagen(vehiculo["id"], ruta)
            except (ErrorApi, OSError):
                fallidas += 1

        if fallidas:
            # El vehiculo ya existe, se puede agregar fotos despues desde "Editar"
            self.etiqueta_error.configure(
                text=f"Se publico, pero {fallidas} imagen(es) no se pudieron subir (max 5 MB, JPG/PNG/WEBP)"
            )
            self.boton_publicar.configure(state="disabled", text="Publicado")
            self.after(2500, lambda: self.app.ir_a("listado"))
            return
        self.app.ir_a("listado")