import customtkinter as ctk

from cliente.api_cliente import ErrorApi
from cliente.estilos import (
    COLOR_FONDO, COLOR_TARJETA, COLOR_CAMPO, COLOR_NARANJA, COLOR_VERDE_CLARO,
    COLOR_TEXTO_CLARO, COLOR_TEXTO_OSCURO, COLOR_ERROR, FUENTE,
)
from cliente.vistas.pantalla_con_header import PantallaConHeader

COLOR_BORDE_TARJETA = "#9AA8BF"


class PerfilView(PantallaConHeader):
    """Edita los datos del usuario: nombre, correo, ciudad, telefono y contrasena."""

    def construir_contenido(self) -> None:
        scroll = ctk.CTkScrollableFrame(self.contenido, fg_color=COLOR_FONDO)
        scroll.pack(fill="both", expand=True, padx=20, pady=10)
        self.crear_boton_volver(scroll).pack(anchor="w")

        marco = ctk.CTkFrame(scroll, fg_color=COLOR_BORDE_TARJETA, corner_radius=18)
        marco.pack(padx=10, pady=(5, 10))
        tarjeta = ctk.CTkFrame(marco, fg_color=COLOR_TARJETA, corner_radius=16)
        tarjeta.pack(padx=8, pady=8)

        ctk.CTkLabel(tarjeta, text="Mi perfil", text_color=COLOR_TEXTO_CLARO,
                     font=(FUENTE, 22, "bold")).grid(row=0, column=0, columnspan=2,
                                                     padx=30, pady=(18, 8), sticky="w")

        u = self.app.sesion.usuario
        self.campos: dict[str, ctk.CTkEntry] = {}
        fila = 1
        for clave, titulo, valor in (
            ("usuario", "Nombre de usuario:", u.get("nombre_usuario")),
            ("correo", "Correo:", u.get("correo")),
            ("ciudad", "Ciudad:", u.get("ciudad")),
            ("telefono", "Telefono:", u.get("telefono")),
        ):
            self.campos[clave] = self._campo(tarjeta, titulo, fila)
            if valor:
                self.campos[clave].insert(0, valor)
            fila += 1

        ctk.CTkLabel(tarjeta, text="Cambiar contrasena (opcional)", text_color=COLOR_VERDE_CLARO,
                     font=(FUENTE, 14, "bold")).grid(row=fila, column=0, columnspan=2,
                                                     padx=30, pady=(14, 2), sticky="w")
        fila += 1
        for clave, titulo in (
            ("actual", "Contrasena actual:"),
            ("nueva", "Contrasena nueva:"),
            ("repetir", "Repetir la nueva:"),
        ):
            self.campos[clave] = self._campo(tarjeta, titulo, fila, oculto=True)
            fila += 1

        self.etiqueta_mensaje = ctk.CTkLabel(tarjeta, text="", text_color=COLOR_ERROR,
                                             font=(FUENTE, 12), wraplength=420)
        self.etiqueta_mensaje.grid(row=fila, column=0, columnspan=2, padx=30, pady=(8, 0), sticky="w")
        fila += 1

        botones = ctk.CTkFrame(tarjeta, fg_color="transparent")
        botones.grid(row=fila, column=0, columnspan=2, padx=30, pady=(6, 18), sticky="e")
        ctk.CTkButton(
            botones, text="Cancelar", width=110, height=36, corner_radius=18,
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

    @staticmethod
    def _campo(padre, titulo: str, fila: int, oculto: bool = False) -> ctk.CTkEntry:
        ctk.CTkLabel(padre, text=titulo, text_color=COLOR_TEXTO_CLARO,
                     font=(FUENTE, 13)).grid(row=fila, column=0, padx=(30, 8), pady=4, sticky="e")
        campo = ctk.CTkEntry(
            padre, width=260, height=30, corner_radius=10, fg_color=COLOR_CAMPO,
            text_color=COLOR_TEXTO_OSCURO, border_color="black", border_width=2,
            show="*" if oculto else "",
        )
        campo.grid(row=fila, column=1, padx=(0, 30), pady=4, sticky="w")
        return campo

    def _mensaje(self, texto: str, error: bool = True) -> None:
        self.etiqueta_mensaje.configure(
            text=texto, text_color=COLOR_ERROR if error else COLOR_VERDE_CLARO
        )

    def guardar(self) -> None:
        c = {k: v.get().strip() if k not in ("actual", "nueva", "repetir") else v.get()
             for k, v in self.campos.items()}

        if len(c["usuario"]) < 3:
            return self._mensaje("El usuario debe tener al menos 3 caracteres")
        if "@" not in c["correo"] or "." not in c["correo"]:
            return self._mensaje("Escribe un correo valido")

        cambios = {
            "nombre_usuario": c["usuario"], "correo": c["correo"],
            "ciudad": c["ciudad"], "telefono": c["telefono"],
        }
        # Si se llena cualquier campo de contrasena, se valida el cambio completo
        if c["actual"] or c["nueva"] or c["repetir"]:
            if not c["actual"]:
                return self._mensaje("Escribe tu contrasena actual")
            if len(c["nueva"]) < 6:
                return self._mensaje("La contrasena nueva debe tener al menos 6 caracteres")
            if c["nueva"] != c["repetir"]:
                return self._mensaje("La contrasena nueva no coincide")
            cambios["contrasena_actual"] = c["actual"]
            cambios["contrasena_nueva"] = c["nueva"]

        self.boton_guardar.configure(state="disabled", text="Guardando...")
        self.update_idletasks()
        try:
            self.app.api.editar_perfil(cambios)
        except ErrorApi as e:
            self._mensaje(str(e))
            return
        finally:
            self.boton_guardar.configure(state="normal", text="Guardar cambios")

        for clave in ("actual", "nueva", "repetir"):
            self.campos[clave].delete(0, "end")
        self.actualizar_usuario_header()
        self._mensaje("Cambios guardados", error=False)
