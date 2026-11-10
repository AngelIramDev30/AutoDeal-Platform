import customtkinter as ctk

from cliente.estilos import (
    COLOR_FONDO, COLOR_HEADER, COLOR_TARJETA, COLOR_TEXTO_CLARO,
    COLOR_TEXTO_OSCURO, FUENTE,
)
from cliente.vistas.pantalla_base import PantallaBase


class PantallaConHeader(PantallaBase):
    """Pantalla con el header del diseno (buscador, botones y usuario)."""

    def construir(self) -> None:
        self._construir_header()
        self.contenido = ctk.CTkFrame(self, fg_color=COLOR_FONDO, corner_radius=0)
        self.contenido.pack(fill="both", expand=True)
        self.construir_contenido()

    def construir_contenido(self) -> None:
        """Cada pantalla hija crea aqui sus widgets dentro de self.contenido."""

    def crear_boton_volver(self, padre) -> ctk.CTkButton:
        """Boton '< Volver' que regresa a la pantalla anterior. Lo empaqueta el que lo llama."""
        return ctk.CTkButton(
            padre, text="< Volver", width=90, height=28, fg_color="transparent", hover=False,
            text_color=COLOR_TEXTO_OSCURO, font=(FUENTE, 13, "underline"),
            command=self.app.volver,
        )

    def _construir_header(self) -> None:
        header = ctk.CTkFrame(self, fg_color=COLOR_HEADER, corner_radius=0, height=120)
        header.pack(fill="x")
        header.pack_propagate(False)
        header.grid_propagate(False)
        header.grid_columnconfigure(0, weight=1)

        # ---- centro: buscador y botones ----
        centro = ctk.CTkFrame(header, fg_color="transparent")
        centro.grid(row=0, column=0, pady=(12, 0))

        self.campo_busqueda = ctk.CTkEntry(
            centro, width=420, height=36, corner_radius=12, fg_color="white",
            text_color=COLOR_TEXTO_OSCURO, border_color="black", border_width=2,
            placeholder_text="Buscar por marca o modelo...",
        )
        self.campo_busqueda.pack(pady=(0, 10))
        self.campo_busqueda.bind("<Return>", lambda e: self._buscar())

        botones = ctk.CTkFrame(centro, fg_color="transparent")
        botones.pack()
        for texto, destino, ancho in (
            ("Inicio", "listado", 90),
            ("Filtros", "filtros", 110),
            ("Publicar vehiculo", "publicar", 140),
            ("Mis publicaciones", "mis_publicaciones", 140),
        ):
            ctk.CTkButton(
                botones, text=texto, width=ancho, height=30, corner_radius=15,
                fg_color=COLOR_TARJETA, hover_color="#3F5873", text_color=COLOR_TEXTO_CLARO,
                font=(FUENTE, 12, "bold"), command=lambda d=destino: self.app.ir_a(d),
            ).pack(side="left", padx=6)

        # ---- derecha: avatar y nombre ----
        nombre = self.app.sesion.usuario["nombre_usuario"]
        usuario = ctk.CTkFrame(header, fg_color="transparent")
        usuario.grid(row=0, column=1, padx=20, pady=(10, 0), sticky="n")

        # Avatar y nombre abren el perfil (para editar los datos del usuario)
        self.boton_avatar = ctk.CTkButton(
            usuario, text=nombre[:1].upper(), width=56, height=56, corner_radius=28,
            fg_color="#D9D9D9", hover_color="#C4C4C4", text_color=COLOR_TEXTO_OSCURO,
            font=(FUENTE, 24, "bold"), command=lambda: self.app.ir_a("perfil"),
        )
        self.boton_avatar.pack()
        self.etiqueta_usuario = ctk.CTkLabel(usuario, text=nombre, text_color=COLOR_TEXTO_CLARO,
                                             font=(FUENTE, 11, "underline"), cursor="hand2")
        self.etiqueta_usuario.pack()
        self.etiqueta_usuario.bind("<Button-1>", lambda e: self.app.ir_a("perfil"))
        ctk.CTkButton(
            usuario, text="Salir", width=50, height=18, fg_color="transparent", hover=False,
            text_color=COLOR_TEXTO_CLARO, font=(FUENTE, 10, "underline"),
            command=self.app.cerrar_sesion,
        ).pack()

    def actualizar_usuario_header(self) -> None:
        """Refresca el avatar y el nombre del header (ej. despues de editar el perfil)."""
        nombre = self.app.sesion.usuario["nombre_usuario"]
        self.boton_avatar.configure(text=nombre[:1].upper())
        self.etiqueta_usuario.configure(text=nombre)

    def _buscar(self) -> None:
        self.app.ir_a("listado", texto=self.campo_busqueda.get().strip())