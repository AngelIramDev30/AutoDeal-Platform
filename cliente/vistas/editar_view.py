import io
from tkinter import filedialog

import customtkinter as ctk
from PIL import Image

from cliente.api_cliente import ErrorApi
from cliente.estilos import (
    COLOR_FONDO, COLOR_TARJETA, COLOR_CAMPO, COLOR_NARANJA, COLOR_TEXTO_CLARO,
    COLOR_TEXTO_OSCURO, COLOR_ERROR, COLOR_VERDE_CLARO, FUENTE,
)
from cliente.vistas.pantalla_con_header import PantallaConHeader

MAX_IMAGENES = 6
COLOR_BORDE_TARJETA = "#9AA8BF"
COLOR_CAJA_IMAGEN = "#8697B5"
ESTADOS = ["Disponible", "Reservado", "Vendido"]


class EditarView(PantallaConHeader):
    """Edita una publicacion propia: datos, precio, estado y fotos nuevas."""

    def construir_contenido(self) -> None:
        self.vehiculo: dict | None = None
        self.rutas_nuevas: list[str] = []
        self.campos: dict[str, ctk.CTkEntry] = {}

        scroll = ctk.CTkScrollableFrame(self.contenido, fg_color=COLOR_FONDO)
        scroll.pack(fill="both", expand=True, padx=20, pady=10)
        self.crear_boton_volver(scroll).pack(anchor="w")
        self.zona = ctk.CTkFrame(scroll, fg_color="transparent")
        self.zona.pack(fill="both", expand=True)

    def al_mostrar(self) -> None:
        self.cargar()

    # ---------- carga ----------
    def cargar(self) -> None:
        try:
            self.vehiculo = self.app.api.detalle_vehiculo(self.datos["vehiculo_id"])
        except KeyError:
            self._mostrar_error("No se indico que vehiculo editar")
            return
        except ErrorApi as e:
            self._mostrar_error(str(e))
            return
        if self.vehiculo["vendedor_id"] != self.app.sesion.usuario["id"]:
            self._mostrar_error("No puedes editar un vehiculo que no es tuyo")
            return
        self._dibujar()

    def _mostrar_error(self, mensaje: str) -> None:
        ctk.CTkLabel(self.zona, text=mensaje, text_color="#B00020",
                     font=(FUENTE, 15)).pack(pady=40)

    # ---------- dibujo ----------
    def _dibujar(self) -> None:
        v = self.vehiculo
        marco = ctk.CTkFrame(self.zona, fg_color=COLOR_BORDE_TARJETA, corner_radius=18)
        marco.pack(fill="x", padx=10, pady=(5, 10))
        tarjeta = ctk.CTkFrame(marco, fg_color=COLOR_TARJETA, corner_radius=16)
        tarjeta.pack(fill="x", padx=8, pady=8)
        tarjeta.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(tarjeta, text="Editar publicacion", text_color=COLOR_TEXTO_CLARO,
                     font=(FUENTE, 22, "bold")).grid(row=0, column=0, columnspan=2,
                                                     padx=25, pady=(18, 4), sticky="w")

        # ---- izquierda: foto actual y boton para agregar ----
        izquierda = ctk.CTkFrame(tarjeta, fg_color="transparent")
        izquierda.grid(row=1, column=0, rowspan=2, padx=20, pady=10, sticky="n")

        self.etiqueta_foto = ctk.CTkLabel(
            izquierda, text="Sin foto", width=240, height=200, corner_radius=14,
            fg_color=COLOR_CAJA_IMAGEN, text_color=COLOR_TEXTO_OSCURO, font=(FUENTE, 14),
        )
        self.etiqueta_foto.pack()
        self._cargar_foto_actual()

        self.etiqueta_cantidad = ctk.CTkLabel(izquierda, text="", text_color=COLOR_TEXTO_CLARO,
                                              font=(FUENTE, 12))
        self.etiqueta_cantidad.pack(pady=(8, 2))
        ctk.CTkButton(
            izquierda, text="+ Agregar imagenes", width=200, height=30, corner_radius=15,
            fg_color=COLOR_CAJA_IMAGEN, hover_color="#7787A5", text_color=COLOR_TEXTO_OSCURO,
            font=(FUENTE, 12, "bold"), command=self.elegir_imagenes,
        ).pack(pady=2)
        ctk.CTkButton(
            izquierda, text="Quitar las nuevas", width=140, height=24, fg_color="transparent",
            hover=False, text_color=COLOR_TEXTO_CLARO, font=(FUENTE, 11, "underline"),
            command=self.quitar_nuevas,
        ).pack()
        self._actualizar_cantidad()

        # ---- derecha: campos ----
        formulario = ctk.CTkFrame(tarjeta, fg_color="transparent")
        formulario.grid(row=1, column=1, sticky="nw", pady=10)

        datos_campos = [
            ("marca", "Marca:"), ("modelo", "Modelo:"), ("anio", "Anio:"),
            ("color", "Color:"), ("kilometraje", "Kilometraje:"),
            ("precio", "Precio (MXN):"), ("ciudad", "Ciudad:"),
        ]
        self.campos = {}
        for fila, (clave, titulo) in enumerate(datos_campos):
            ctk.CTkLabel(formulario, text=titulo, text_color=COLOR_TEXTO_CLARO,
                         font=(FUENTE, 13)).grid(row=fila, column=0, sticky="e", padx=(0, 8), pady=3)
            campo = ctk.CTkEntry(
                formulario, width=240, height=30, corner_radius=10, fg_color=COLOR_CAMPO,
                text_color=COLOR_TEXTO_OSCURO, border_color="black", border_width=2,
            )
            campo.grid(row=fila, column=1, pady=3, sticky="w")
            valor = v.get(clave)
            if valor not in (None, ""):
                if clave == "precio" and float(valor).is_integer():
                    valor = int(valor)
                campo.insert(0, str(valor))
            self.campos[clave] = campo

        fila = len(datos_campos)
        ctk.CTkLabel(formulario, text="Estado:", text_color=COLOR_TEXTO_CLARO,
                     font=(FUENTE, 13)).grid(row=fila, column=0, sticky="e", padx=(0, 8), pady=3)
        self.menu_estado = ctk.CTkOptionMenu(
            formulario, values=ESTADOS, width=240, height=30, corner_radius=10,
            fg_color=COLOR_CAMPO, button_color=COLOR_CAJA_IMAGEN, button_hover_color="#7787A5",
            text_color=COLOR_TEXTO_OSCURO, dropdown_fg_color="white",
            dropdown_text_color=COLOR_TEXTO_OSCURO, font=(FUENTE, 13),
        )
        self.menu_estado.set(v["estado"] if v["estado"] in ESTADOS else "Disponible")
        self.menu_estado.grid(row=fila, column=1, pady=3, sticky="w")

        # ---- descripcion ----
        ctk.CTkLabel(tarjeta, text="Descripcion:", text_color=COLOR_TEXTO_CLARO,
                     font=(FUENTE, 13)).grid(row=3, column=0, columnspan=2, sticky="w", padx=25)
        self.texto_descripcion = ctk.CTkTextbox(
            tarjeta, height=90, corner_radius=10, fg_color=COLOR_CAMPO,
            text_color=COLOR_TEXTO_OSCURO, border_color="black", border_width=2,
        )
        self.texto_descripcion.grid(row=4, column=0, columnspan=2, sticky="ew", padx=25, pady=(2, 8))
        self.texto_descripcion.insert("1.0", v.get("descripcion") or "")

        # ---- pie ----
        self.etiqueta_error = ctk.CTkLabel(tarjeta, text="", text_color=COLOR_ERROR,
                                           font=(FUENTE, 12), wraplength=600)
        self.etiqueta_error.grid(row=5, column=0, columnspan=2, sticky="w", padx=25)

        botones = ctk.CTkFrame(tarjeta, fg_color="transparent")
        botones.grid(row=6, column=0, columnspan=2, sticky="e", padx=25, pady=(4, 18))
        ctk.CTkButton(
            botones, text="Cancelar", width=120, height=36, corner_radius=18,
            fg_color="transparent", border_width=2, border_color=COLOR_TEXTO_CLARO,
            hover_color="#3F5873", text_color=COLOR_TEXTO_CLARO, font=(FUENTE, 14),
            command=self.app.volver,
        ).pack(side="left", padx=8)
        self.boton_guardar = ctk.CTkButton(
            botones, text="Guardar cambios", width=160, height=36, corner_radius=18,
            fg_color=COLOR_NARANJA, hover_color="#D4763F", text_color=COLOR_TEXTO_OSCURO,
            font=(FUENTE, 14, "bold"), command=self.guardar,
        )
        self.boton_guardar.pack(side="left", padx=8)

    # ---------- fotos ----------
    def _cargar_foto_actual(self) -> None:
        imagenes = self.vehiculo.get("imagenes", [])
        if not imagenes:
            return
        principal = next((i for i in imagenes if i["es_principal"]), imagenes[0])
        contenido = self.app.api.descargar_imagen(principal["archivo"])
        if contenido is None:
            return
        try:
            foto = Image.open(io.BytesIO(contenido)).convert("RGB")
        except OSError:
            return
        escala = min(240 / foto.width, 200 / foto.height)
        tam = (max(1, int(foto.width * escala)), max(1, int(foto.height * escala)))
        self.etiqueta_foto.configure(image=ctk.CTkImage(foto, size=tam), text="")

    def _actualizar_cantidad(self) -> None:
        actuales = len(self.vehiculo.get("imagenes", []))
        texto = f"{actuales + len(self.rutas_nuevas)} de {MAX_IMAGENES} imagenes"
        if self.rutas_nuevas:
            texto += f" ({len(self.rutas_nuevas)} nuevas)"
        self.etiqueta_cantidad.configure(text=texto)

    def elegir_imagenes(self) -> None:
        espacio = MAX_IMAGENES - len(self.vehiculo.get("imagenes", [])) - len(self.rutas_nuevas)
        if espacio <= 0:
            self.etiqueta_error.configure(text=f"Ya tiene el maximo de {MAX_IMAGENES} imagenes")
            return
        rutas = filedialog.askopenfilenames(
            title="Elige las fotos nuevas",
            filetypes=[("Imagenes", "*.jpg *.jpeg *.png *.webp")],
        )
        if not rutas:
            return
        self.rutas_nuevas.extend(rutas[:espacio])
        self.etiqueta_error.configure(
            text=f"Solo caben {espacio} imagen(es) mas" if len(rutas) > espacio else ""
        )
        self._actualizar_cantidad()

    def quitar_nuevas(self) -> None:
        self.rutas_nuevas.clear()
        self._actualizar_cantidad()

    # ---------- guardar ----------
    def _leer_datos(self) -> dict | None:
        c = {k: v.get().strip() for k, v in self.campos.items()}

        if len(c["marca"]) < 2:
            return self._error("Escribe la marca")
        if not c["modelo"]:
            return self._error("Escribe el modelo")
        if len(c["color"]) < 2:
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
            "estado": self.menu_estado.get(),
        }

    def _error(self, mensaje: str) -> None:
        self.etiqueta_error.configure(text=mensaje)
        return None

    def guardar(self) -> None:
        self.etiqueta_error.configure(text="")
        nuevos = self._leer_datos()
        if nuevos is None:
            return

        # Solo se envia lo que realmente cambio
        cambios = {k: val for k, val in nuevos.items() if val != self.vehiculo.get(k)}

        self.boton_guardar.configure(state="disabled", text="Guardando...")
        self.update_idletasks()
        try:
            if cambios:
                self.app.api.editar_vehiculo(self.vehiculo["id"], cambios)
        except ErrorApi as e:
            self.etiqueta_error.configure(text=str(e))
            self.boton_guardar.configure(state="normal", text="Guardar cambios")
            return

        fallidas = 0
        for ruta in self.rutas_nuevas:
            try:
                self.app.api.subir_imagen(self.vehiculo["id"], ruta)
            except (ErrorApi, OSError):
                fallidas += 1

        if fallidas:
            self.etiqueta_error.configure(
                text=f"Se guardo, pero {fallidas} imagen(es) no se pudieron subir (max 5 MB, JPG/PNG/WEBP)"
            )
            self.boton_guardar.configure(text="Guardado")
            self.after(2500, self.app.volver)
            return
        self.app.volver()
