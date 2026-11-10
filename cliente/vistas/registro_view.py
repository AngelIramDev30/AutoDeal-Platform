import customtkinter as ctk

from cliente.api_cliente import ErrorApi
from cliente.estilos import (
    COLOR_TARJETA, COLOR_CAMPO, COLOR_VERDE_CLARO, COLOR_TEXTO_CLARO,
    COLOR_TEXTO_OSCURO, COLOR_ERROR, FUENTE,
)
from cliente.vistas.pantalla_base import PantallaBase


class RegistroView(PantallaBase):
    def construir(self) -> None:
        tarjeta = ctk.CTkFrame(self, fg_color=COLOR_TARJETA, corner_radius=20, width=420, height=640)
        tarjeta.place(relx=0.5, rely=0.5, anchor="center")
        tarjeta.pack_propagate(False)

        ctk.CTkLabel(tarjeta, text="Crear cuenta", text_color=COLOR_TEXTO_CLARO,
                     font=(FUENTE, 24, "bold")).pack(pady=(24, 14))

        self.campos = {
            "usuario": self._agregar_campo(tarjeta, "Nombre de usuario"),
            "correo": self._agregar_campo(tarjeta, "Correo"),
            "contrasena": self._agregar_campo(tarjeta, "Contrasena (minimo 6)", oculto=True),
            "ciudad": self._agregar_campo(tarjeta, "Ciudad (opcional)"),
            "telefono": self._agregar_campo(tarjeta, "Telefono (opcional)"),
        }

        self.etiqueta_error = ctk.CTkLabel(
            tarjeta, text="", text_color=COLOR_ERROR, font=(FUENTE, 12), wraplength=330,
        )
        self.etiqueta_error.pack(pady=(4, 4))

        self.boton_registrar = ctk.CTkButton(
            tarjeta, text="Registrarme", width=170, height=38, corner_radius=19,
            fg_color=COLOR_VERDE_CLARO, hover_color="#A5C97B", text_color=COLOR_TEXTO_OSCURO,
            font=(FUENTE, 15, "bold"), command=self.registrar,
        )
        self.boton_registrar.pack(pady=(4, 8))

        ctk.CTkButton(
            tarjeta, text="Ya tengo cuenta", fg_color="transparent", hover=False,
            text_color=COLOR_TEXTO_CLARO, font=(FUENTE, 12, "underline"),
            command=lambda: self.app.ir_a("login"),
        ).pack()

    @staticmethod
    def _agregar_campo(padre, titulo: str, oculto: bool = False) -> ctk.CTkEntry:
        ctk.CTkLabel(padre, text=titulo, text_color=COLOR_TEXTO_CLARO,
                     font=(FUENTE, 14)).pack(pady=(6, 0))
        campo = ctk.CTkEntry(
            padre, width=300, height=34, corner_radius=10, fg_color=COLOR_CAMPO,
            text_color=COLOR_TEXTO_OSCURO, border_color="black", border_width=2,
            show="*" if oculto else "",
        )
        campo.pack(pady=(2, 0))
        return campo

    def registrar(self) -> None:
        usuario = self.campos["usuario"].get().strip()
        correo = self.campos["correo"].get().strip()
        contrasena = self.campos["contrasena"].get()
        ciudad = self.campos["ciudad"].get().strip()
        telefono = self.campos["telefono"].get().strip()

        # Validaciones basicas antes de molestar al servidor
        if len(usuario) < 3:
            self.etiqueta_error.configure(text="El usuario debe tener al menos 3 caracteres")
            return
        if "@" not in correo or "." not in correo:
            self.etiqueta_error.configure(text="Escribe un correo valido")
            return
        if len(contrasena) < 6:
            self.etiqueta_error.configure(text="La contrasena debe tener al menos 6 caracteres")
            return

        self.boton_registrar.configure(state="disabled", text="Creando...")
        self.update_idletasks()
        try:
            self.app.api.registrar(usuario, correo, contrasena, ciudad, telefono)
        except ErrorApi as e:
            self.etiqueta_error.configure(text=str(e))
            self.boton_registrar.configure(state="normal", text="Registrarme")
            return
        self.app.ir_a("listado")