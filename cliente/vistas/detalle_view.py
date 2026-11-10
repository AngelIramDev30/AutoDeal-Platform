import io
from tkinter import messagebox

import customtkinter as ctk
from PIL import Image

from cliente.api_cliente import ErrorApi
from cliente.estilos import (
    COLOR_FONDO, COLOR_TARJETA, COLOR_VERDE, COLOR_VERDE_CLARO, COLOR_NARANJA,
    COLOR_TEXTO_CLARO, COLOR_TEXTO_OSCURO, FUENTE,
)
from cliente.vistas.pantalla_con_header import PantallaConHeader

COLOR_BORDE_TARJETA = "#9AA8BF"
COLOR_CAJA_IMAGEN = "#8697B5"
TAM_FOTO = (460, 310)    # recuadro de la foto grande
TAM_MINIATURA = (70, 50)
_cache_fotos: dict[str, tuple[ctk.CTkImage, ctk.CTkImage]] = {}  # archivo -> (grande, miniatura)


class DetalleView(PantallaConHeader):
    """Detalle de un vehiculo: fotos, datos, Comprar y Contactar."""

    def construir_contenido(self) -> None:
        self.vehiculo: dict | None = None
        self.imagenes: list[dict] = []
        self.miniaturas: list[ctk.CTkButton] = []

        # Todo va dentro de un frame con scroll por si la ventana es chica
        self.scroll = ctk.CTkScrollableFrame(self.contenido, fg_color=COLOR_FONDO)
        self.scroll.pack(fill="both", expand=True, padx=20, pady=10)

        self.crear_boton_volver(self.scroll).pack(anchor="w")

        self.zona = ctk.CTkFrame(self.scroll, fg_color="transparent")
        self.zona.pack(fill="both", expand=True)

    def al_mostrar(self) -> None:
        self.cargar()

    # ---------- carga de datos ----------
    def cargar(self) -> None:
        for hijo in self.zona.winfo_children():
            hijo.destroy()

        try:
            self.vehiculo = self.app.api.detalle_vehiculo(self.datos["vehiculo_id"])
        except KeyError:
            self._mostrar_error("No se indico que vehiculo mostrar")
            return
        except ErrorApi as e:
            self._mostrar_error(str(e))
            return
        self._dibujar()

    def _mostrar_error(self, mensaje: str) -> None:
        ctk.CTkLabel(self.zona, text=mensaje, text_color="#B00020",
                     font=(FUENTE, 15)).pack(pady=40)

    # ---------- dibujo ----------
    def _dibujar(self) -> None:
        v = self.vehiculo
        marco = ctk.CTkFrame(self.zona, fg_color=COLOR_BORDE_TARJETA, corner_radius=18)
        marco.pack(fill="x", pady=(5, 10))
        tarjeta = ctk.CTkFrame(marco, fg_color=COLOR_TARJETA, corner_radius=16)
        tarjeta.pack(fill="x", padx=8, pady=8)
        tarjeta.grid_columnconfigure(1, weight=1)

        self._construir_galeria(tarjeta)
        self._construir_datos(tarjeta, v)
        self._construir_descripcion(tarjeta, v)
        self._construir_acciones(tarjeta, v)

    def _construir_galeria(self, tarjeta) -> None:
        galeria = ctk.CTkFrame(tarjeta, fg_color="transparent")
        galeria.grid(row=0, column=0, padx=20, pady=20, sticky="n")

        self.etiqueta_foto = ctk.CTkLabel(
            galeria, text="Sin foto", width=TAM_FOTO[0], height=TAM_FOTO[1],
            fg_color=COLOR_CAJA_IMAGEN, corner_radius=14,
            text_color=COLOR_TEXTO_OSCURO, font=(FUENTE, 16),
        )
        self.etiqueta_foto.pack()

        # La imagen principal va primero
        imagenes = sorted(self.vehiculo.get("imagenes", []), key=lambda i: not i["es_principal"])
        self.imagenes = []
        self.miniaturas = []
        if not imagenes:
            return

        fila = ctk.CTkFrame(galeria, fg_color="transparent")
        fila.pack(pady=(10, 0))
        for imagen in imagenes:
            grande, mini = self._obtener_fotos(imagen["archivo"])
            if grande is None:  # no se pudo descargar: se omite
                continue
            indice = len(self.imagenes)
            self.imagenes.append(imagen)
            boton = ctk.CTkButton(
                fila, text="", image=mini, width=TAM_MINIATURA[0], height=TAM_MINIATURA[1],
                fg_color=COLOR_CAJA_IMAGEN, hover_color="#7787A5", corner_radius=8,
                border_width=2, border_color=COLOR_TARJETA,
                command=lambda i=indice: self.mostrar_foto(i),
            )
            boton.pack(side="left", padx=3)
            self.miniaturas.append(boton)

        if self.imagenes:
            self.mostrar_foto(0)

    def _obtener_fotos(self, archivo: str):
        """Descarga la foto una sola vez y devuelve (grande, miniatura)."""
        if archivo not in _cache_fotos:
            contenido = self.app.api.descargar_imagen(archivo)
            if contenido is None:
                return None, None
            try:
                foto = Image.open(io.BytesIO(contenido)).convert("RGB")
            except OSError:
                return None, None
            # La foto grande conserva la proporcion dentro del recuadro
            ancho, alto = foto.size
            escala = min(TAM_FOTO[0] / ancho, TAM_FOTO[1] / alto)
            tam_grande = (max(1, int(ancho * escala)), max(1, int(alto * escala)))
            _cache_fotos[archivo] = (
                ctk.CTkImage(foto, size=tam_grande),
                ctk.CTkImage(foto, size=TAM_MINIATURA),
            )
        return _cache_fotos[archivo]

    def mostrar_foto(self, indice: int) -> None:
        grande, _ = self._obtener_fotos(self.imagenes[indice]["archivo"])
        if grande is None:
            return
        self.etiqueta_foto.configure(image=grande, text="")
        for i, boton in enumerate(self.miniaturas):
            boton.configure(border_color=COLOR_VERDE_CLARO if i == indice else COLOR_TARJETA)

    def _construir_datos(self, tarjeta, v: dict) -> None:
        datos = ctk.CTkFrame(tarjeta, fg_color="transparent")
        datos.grid(row=0, column=1, padx=(0, 20), pady=20, sticky="nw")

        ctk.CTkLabel(
            datos, text=f"{v['marca']} {v['modelo']}", text_color=COLOR_TEXTO_CLARO,
            font=(FUENTE, 24, "bold"), anchor="w",
        ).pack(anchor="w")
        ctk.CTkLabel(
            datos, text=f"{v['precio']:,.0f} MXN", text_color=COLOR_VERDE_CLARO,
            font=(FUENTE, 22, "bold"), anchor="w",
        ).pack(anchor="w", pady=(0, 10))

        if v["estado"] != "Disponible":
            ctk.CTkLabel(datos, text=v["estado"].upper(), text_color=COLOR_NARANJA,
                         font=(FUENTE, 15, "bold")).pack(anchor="w", pady=(0, 8))

        for titulo, valor in (
            ("Anio", v["anio"]),
            ("Color", v["color"]),
            ("Kilometraje", f"{v['kilometraje']:,} km"),
            ("Ciudad", v.get("ciudad") or "No especificada"),
            ("Estado", v["estado"]),
        ):
            ctk.CTkLabel(
                datos, text=f"{titulo}: {valor}", text_color=COLOR_TEXTO_CLARO,
                font=(FUENTE, 15), anchor="w",
            ).pack(anchor="w", pady=2)

    def _construir_descripcion(self, tarjeta, v: dict) -> None:
        ctk.CTkLabel(
            tarjeta, text="Descripcion", text_color=COLOR_TEXTO_CLARO,
            font=(FUENTE, 14, "bold"),
        ).grid(row=1, column=0, columnspan=2, padx=20, sticky="w")

        texto = v.get("descripcion") or "El vendedor no agrego descripcion."
        ctk.CTkLabel(
            tarjeta, text=texto, text_color=COLOR_TEXTO_CLARO, font=(FUENTE, 13),
            anchor="w", justify="left", wraplength=800,
        ).grid(row=2, column=0, columnspan=2, padx=20, pady=(2, 10), sticky="w")

    def _construir_acciones(self, tarjeta, v: dict) -> None:
        acciones = ctk.CTkFrame(tarjeta, fg_color="transparent")
        acciones.grid(row=3, column=0, columnspan=2, padx=20, pady=(0, 20), sticky="w")

        if v["vendedor_id"] == self.app.sesion.usuario["id"]:
            ctk.CTkLabel(acciones, text="Este vehiculo es tuyo",
                         text_color=COLOR_VERDE_CLARO, font=(FUENTE, 14, "italic")).pack(anchor="w")
            ctk.CTkButton(
                acciones, text="Editar publicacion", width=170, height=36, corner_radius=18,
                fg_color=COLOR_NARANJA, hover_color="#D17A4E", text_color=COLOR_TEXTO_CLARO,
                font=(FUENTE, 14, "bold"),
                command=lambda: self.app.ir_a("editar", vehiculo_id=v["id"]),
            ).pack(anchor="w", pady=(8, 0))
            return

        botones = ctk.CTkFrame(acciones, fg_color="transparent")
        botones.pack(anchor="w")

        disponible = v["estado"] == "Disponible"
        ctk.CTkButton(
            botones, text="Comprar" if disponible else v["estado"], width=160, height=38,
            corner_radius=19, fg_color=COLOR_VERDE, hover_color="#5C9A67",
            text_color=COLOR_TEXTO_CLARO, font=(FUENTE, 15, "bold"),
            state="normal" if disponible else "disabled", command=self.comprar,
        ).pack(side="left", padx=(0, 12))

        ctk.CTkButton(
            botones, text="Contactar", width=160, height=38, corner_radius=19,
            fg_color=COLOR_NARANJA, hover_color="#D17A4E", text_color=COLOR_TEXTO_CLARO,
            font=(FUENTE, 15, "bold"), command=self.contactar,
        ).pack(side="left")

        # Aqui aparecen los datos del vendedor o los mensajes de error
        self.etiqueta_info = ctk.CTkLabel(
            acciones, text="", text_color=COLOR_TEXTO_CLARO, font=(FUENTE, 14),
            anchor="w", justify="left",
        )
        self.etiqueta_info.pack(anchor="w", pady=(12, 0))

    # ---------- acciones ----------
    def contactar(self) -> None:
        try:
            c = self.app.api.contacto_vendedor(self.vehiculo["id"])
        except ErrorApi as e:
            self.etiqueta_info.configure(text=str(e), text_color="#FF9A9A")
            return
        self.etiqueta_info.configure(
            text=(
                f"Vendedor: {c['nombre_usuario']}\n"
                f"Telefono: {c.get('telefono') or 'No registrado'}\n"
                f"Correo: {c['correo']}"
            ),
            text_color=COLOR_TEXTO_CLARO,
        )

    def comprar(self) -> None:
        v = self.vehiculo
        if not messagebox.askyesno(
            "Confirmar", f"Quieres reservar el {v['marca']} {v['modelo']}?"
        ):
            return
        try:
            self.app.api.comprar_vehiculo(v["id"])
        except ErrorApi as e:
            messagebox.showerror("No se pudo comprar", str(e))
            return
        messagebox.showinfo(
            "Listo", "El vehiculo quedo como Reservado.\nUsa Contactar para hablar con el vendedor."
        )
        self.cargar()  # recarga para mostrar el nuevo estado
