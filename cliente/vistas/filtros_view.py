import customtkinter as ctk

from cliente.api_cliente import ErrorApi
from cliente.estilos import (
    COLOR_FONDO, COLOR_TARJETA, COLOR_CAMPO, COLOR_VERDE_CLARO, COLOR_NARANJA,
    COLOR_TEXTO_CLARO, COLOR_TEXTO_OSCURO, COLOR_ERROR, FUENTE,
)
from cliente.vistas.pantalla_con_header import PantallaConHeader

COLOR_BORDE_TARJETA = "#9AA8BF"
TODAS = "Todas"

# Texto que ve el usuario -> codigo que entiende el servidor
ORDENES = {
    "Mas recientes": "recientes",
    "Precio: menor a mayor": "precio_asc",
    "Precio: mayor a menor": "precio_desc",
    "Anio: mas nuevo primero": "anio_desc",
    "Kilometraje: menor primero": "km_asc",
}


class FiltrosView(PantallaConHeader):
    """Pantalla para filtrar el listado. Al aplicar, abre el listado con esos filtros."""

    def construir_contenido(self) -> None:
        self.campos: dict[str, ctk.CTkEntry] = {}

        scroll = ctk.CTkScrollableFrame(self.contenido, fg_color=COLOR_FONDO)
        scroll.pack(fill="both", expand=True, padx=20, pady=10)
        self.crear_boton_volver(scroll).pack(anchor="w")

        marco = ctk.CTkFrame(scroll, fg_color=COLOR_BORDE_TARJETA, corner_radius=18)
        marco.pack(fill="x", padx=10, pady=(5, 10))
        tarjeta = ctk.CTkFrame(marco, fg_color=COLOR_TARJETA, corner_radius=16)
        tarjeta.pack(fill="x", padx=8, pady=8)
        tarjeta.grid_columnconfigure((1, 2), weight=1)

        ctk.CTkLabel(tarjeta, text="Filtros", text_color=COLOR_TEXTO_CLARO,
                     font=(FUENTE, 22, "bold")).grid(row=0, column=0, columnspan=3,
                                                     padx=25, pady=(18, 8), sticky="w")

        fila = 1
        # ---- marca (lista con las marcas que hay publicadas) ----
        self._etiqueta(tarjeta, "Marca:", fila)
        self.menu_marca = self._menu(tarjeta, [TODAS] + self._cargar_marcas())
        self.menu_marca.grid(row=fila, column=1, columnspan=2, padx=8, pady=6, sticky="w")

        # ---- rangos: dos campos (minimo y maximo) por fila ----
        fila += 1
        self._fila_rango(tarjeta, fila, "Precio (MXN):", "precio_min", "precio_max")
        fila += 1
        self._fila_rango(tarjeta, fila, "Anio:", "anio_min", "anio_max")

        # ---- kilometraje maximo ----
        fila += 1
        self._etiqueta(tarjeta, "Kilometraje maximo:", fila)
        self.campos["km_max"] = self._campo(tarjeta, "Ej. 80000")
        self.campos["km_max"].grid(row=fila, column=1, padx=8, pady=6, sticky="w")

        # ---- texto libre ----
        fila += 1
        self._etiqueta(tarjeta, "Color:", fila)
        self.campos["color"] = self._campo(tarjeta, "Ej. Rojo")
        self.campos["color"].grid(row=fila, column=1, padx=8, pady=6, sticky="w")

        fila += 1
        self._etiqueta(tarjeta, "Ciudad:", fila)
        self.campos["ciudad"] = self._campo(tarjeta, "Ej. Hermosillo")
        self.campos["ciudad"].grid(row=fila, column=1, padx=8, pady=6, sticky="w")

        # ---- orden ----
        fila += 1
        self._etiqueta(tarjeta, "Ordenar por:", fila)
        self.menu_orden = self._menu(tarjeta, list(ORDENES))
        self.menu_orden.grid(row=fila, column=1, columnspan=2, padx=8, pady=6, sticky="w")

        # ---- ocultar reservados ----
        fila += 1
        self.solo_disponibles = ctk.CTkCheckBox(
            tarjeta, text="Ocultar vehiculos reservados", text_color=COLOR_TEXTO_CLARO,
            font=(FUENTE, 13), fg_color=COLOR_VERDE_CLARO, hover_color="#A5C97B",
            checkmark_color=COLOR_TEXTO_OSCURO,
        )
        self.solo_disponibles.grid(row=fila, column=0, columnspan=3, padx=25, pady=(8, 4), sticky="w")

        # ---- error y botones ----
        fila += 1
        self.etiqueta_error = ctk.CTkLabel(tarjeta, text="", text_color=COLOR_ERROR,
                                           font=(FUENTE, 12), wraplength=600)
        self.etiqueta_error.grid(row=fila, column=0, columnspan=3, padx=25, sticky="w")

        fila += 1
        botones = ctk.CTkFrame(tarjeta, fg_color="transparent")
        botones.grid(row=fila, column=0, columnspan=3, padx=25, pady=(6, 18), sticky="e")
        ctk.CTkButton(
            botones, text="Limpiar", width=120, height=36, corner_radius=18,
            fg_color="transparent", border_width=2, border_color=COLOR_TEXTO_CLARO,
            hover_color="#3F5873", text_color=COLOR_TEXTO_CLARO, font=(FUENTE, 14),
            command=self.limpiar,
        ).pack(side="left", padx=8)
        ctk.CTkButton(
            botones, text="Aplicar filtros", width=150, height=36, corner_radius=18,
            fg_color=COLOR_NARANJA, hover_color="#D4763F", text_color=COLOR_TEXTO_OSCURO,
            font=(FUENTE, 14, "bold"), command=self.aplicar,
        ).pack(side="left", padx=8)

    def al_mostrar(self) -> None:
        self._rellenar(self._filtros_previos())

    # ---------- widgets auxiliares ----------
    def _etiqueta(self, padre, texto: str, fila: int) -> None:
        ctk.CTkLabel(padre, text=texto, text_color=COLOR_TEXTO_CLARO,
                     font=(FUENTE, 14)).grid(row=fila, column=0, padx=(25, 8), pady=6, sticky="e")

    def _campo(self, padre, ayuda: str = "") -> ctk.CTkEntry:
        return ctk.CTkEntry(
            padre, width=170, height=30, corner_radius=10, fg_color=COLOR_CAMPO,
            text_color=COLOR_TEXTO_OSCURO, border_color="black", border_width=2,
            placeholder_text=ayuda, placeholder_text_color="#6B6B6B",
        )

    def _menu(self, padre, valores: list[str]) -> ctk.CTkOptionMenu:
        return ctk.CTkOptionMenu(
            padre, values=valores, width=240, height=30, corner_radius=10,
            fg_color=COLOR_CAMPO, button_color="#8697B5", button_hover_color="#7787A5",
            text_color=COLOR_TEXTO_OSCURO, dropdown_fg_color="white",
            dropdown_text_color=COLOR_TEXTO_OSCURO, font=(FUENTE, 13),
        )

    def _fila_rango(self, padre, fila: int, titulo: str, clave_min: str, clave_max: str) -> None:
        self._etiqueta(padre, titulo, fila)
        self.campos[clave_min] = self._campo(padre, "Desde")
        self.campos[clave_min].grid(row=fila, column=1, padx=8, pady=6, sticky="w")
        self.campos[clave_max] = self._campo(padre, "Hasta")
        self.campos[clave_max].grid(row=fila, column=2, padx=8, pady=6, sticky="w")

    def _cargar_marcas(self) -> list[str]:
        try:
            return self.app.api.listar_marcas()
        except ErrorApi:
            return []  # sin lista de marcas se puede seguir usando el resto de filtros

    # ---------- filtros previos ----------
    def _filtros_previos(self) -> dict:
        """Si venimos del listado, recupera los filtros que tenia para mostrarlos."""
        anterior = self.app.anterior
        if anterior and anterior[0] == "listado":
            return dict(anterior[1])
        return {}

    def _rellenar(self, filtros: dict) -> None:
        for clave, campo in self.campos.items():
            campo.delete(0, "end")
            valor = filtros.get(clave)
            if valor not in (None, ""):
                if isinstance(valor, float) and valor.is_integer():
                    valor = int(valor)  # 200000.0 se muestra como 200000
                campo.insert(0, str(valor))

        marca = filtros.get("marca")
        self.menu_marca.set(marca if marca in self.menu_marca.cget("values") else TODAS)

        codigo_a_texto = {codigo: texto for texto, codigo in ORDENES.items()}
        self.menu_orden.set(codigo_a_texto.get(filtros.get("orden"), "Mas recientes"))

        if filtros.get("solo_disponibles"):
            self.solo_disponibles.select()
        else:
            self.solo_disponibles.deselect()

    # ---------- acciones ----------
    def limpiar(self) -> None:
        self.etiqueta_error.configure(text="")
        self._rellenar({})

    def _numero(self, clave: str, entero: bool, nombre: str):
        """Lee un campo numerico. Vacio -> None. Si no es numero, lanza ValueError con el mensaje."""
        texto = self.campos[clave].get().strip().replace(",", "")
        if not texto:
            return None
        try:
            valor = int(texto) if entero else float(texto)
        except ValueError:
            raise ValueError(f"{nombre} debe ser un numero")
        if valor < 0:
            raise ValueError(f"{nombre} no puede ser negativo")
        return valor

    def aplicar(self) -> None:
        self.etiqueta_error.configure(text="")
        try:
            filtros = {
                "precio_min": self._numero("precio_min", False, "El precio minimo"),
                "precio_max": self._numero("precio_max", False, "El precio maximo"),
                "anio_min": self._numero("anio_min", True, "El anio inicial"),
                "anio_max": self._numero("anio_max", True, "El anio final"),
                "km_max": self._numero("km_max", True, "El kilometraje"),
            }
        except ValueError as e:
            self.etiqueta_error.configure(text=str(e))
            return

        for minimo, maximo, nombre in (
            ("precio_min", "precio_max", "precio"),
            ("anio_min", "anio_max", "anio"),
        ):
            if filtros[minimo] is not None and filtros[maximo] is not None \
                    and filtros[minimo] > filtros[maximo]:
                self.etiqueta_error.configure(text=f"En {nombre}, el minimo es mayor que el maximo")
                return

        marca = self.menu_marca.get()
        filtros["marca"] = None if marca == TODAS else marca
        filtros["color"] = self.campos["color"].get().strip() or None
        filtros["ciudad"] = self.campos["ciudad"].get().strip() or None
        filtros["orden"] = ORDENES[self.menu_orden.get()]
        filtros["solo_disponibles"] = "true" if self.solo_disponibles.get() else None

        # Se conserva la busqueda por texto que hubiera antes
        texto = self._filtros_previos().get("texto")
        if texto:
            filtros["texto"] = texto

        # Se quitan los vacios para que el listado reciba solo lo que importa
        filtros = {k: v for k, v in filtros.items() if v is not None}
        self.app.ir_a("listado", **filtros)
