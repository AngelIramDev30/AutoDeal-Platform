import customtkinter as ctk

from cliente.api_cliente import ErrorApi
from cliente.estilos import (
    COLOR_TARJETA, COLOR_CAMPO, COLOR_VERDE_CLARO, COLOR_TEXTO_CLARO,
    COLOR_TEXTO_OSCURO, COLOR_ERROR, FUENTE,
)
from cliente.vistas.pantalla_base import PantallaBase


class LoginView(PantallaBase):
    def construir(self) -> None:
        tarjeta = ctk.CTkFrame(self, fg_color=COLOR_TARJETA, corner_radius=20, width=380, height=500)
        tarjeta.place(relx=0.5, rely=0.5, anchor="center")
        tarjeta.pack_propagate(False)

        ctk.CTkLabel(
            tarjeta, text="A", width=80, height=80, corner_radius=40,
            fg_color="#D9D9D9", text_color=COLOR_TEXTO_OSCURO, font=(FUENTE, 36, "bold"),
        ).pack(pady=(30, 15))

        ctk.CTkLabel(tarjeta, text="Nombre de usuario", text_color=COLOR_TEXTO_CLARO,
                     font=(FUENTE, 16)).pack()
        self.campo_usuario = self._crear_campo(tarjeta)
        self.campo_usuario.pack(pady=(4, 12))

        ctk.CTkLabel(tarjeta, text="Contrasena", text_color=COLOR_TEXTO_CLARO,
                     font=(FUENTE, 16)).pack()
        self.campo_contrasena = self._crear_campo(tarjeta, oculto=True)
        self.campo_contrasena.pack(pady=(4, 8))

        self.etiqueta_error = ctk.CTkLabel(
            tarjeta, text="", text_color=COLOR_ERROR, font=(FUENTE, 12), wraplength=300,
        )
        self.etiqueta_error.pack(pady=(0, 6))

        self.boton_entrar = ctk.CTkButton(
            tarjeta, text="Entrar", width=150, height=38, corner_radius=19,
            fg_color=COLOR_VERDE_CLARO, hover_color="#A5C97B", text_color=COLOR_TEXTO_OSCURO,
            font=(FUENTE, 15, "bold"), command=self.entrar,
        )
        self.boton_entrar.pack(pady=(4, 10))

        ctk.CTkButton(
            tarjeta, text="Crear cuenta nueva", fg_color="transparent", hover=False,
            text_color=COLOR_TEXTO_CLARO, font=(FUENTE, 12, "underline"),
            command=lambda: self.app.ir_a("registro"),
        ).pack()

        # Enter en cualquiera de los dos campos equivale a pulsar "Entrar"
        self.campo_usuario.bind("<Return>", lambda e: self.entrar())
        self.campo_contrasena.bind("<Return>", lambda e: self.entrar())

    @staticmethod
    def _crear_campo(padre, oculto: bool = False) -> ctk.CTkEntry:
        return ctk.CTkEntry(
            padre, width=270, height=36, corner_radius=10, fg_color=COLOR_CAMPO,
            text_color=COLOR_TEXTO_OSCURO, border_color="black", border_width=2,
            show="*" if oculto else "",
        )

    def al_mostrar(self) -> None:
        self.campo_usuario.focus()

    def entrar(self) -> None:
        usuario = self.campo_usuario.get().strip()
        contrasena = self.campo_contrasena.get()
        if not usuario or not contrasena:
            self.etiqueta_error.configure(text="Escribe tu usuario y contrasena")
            return

        self.boton_entrar.configure(state="disabled", text="Entrando...")
        self.update_idletasks()  # fuerza a dibujar el cambio antes de la peticion
        try:
            self.app.api.iniciar_sesion(usuario, contrasena)
        except ErrorApi as e:
            self.etiqueta_error.configure(text=str(e))
            self.boton_entrar.configure(state="normal", text="Entrar")
            return
        self.app.ir_a("listado")