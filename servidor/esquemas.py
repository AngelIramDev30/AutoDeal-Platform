from pydantic import BaseModel, Field


class RegistroEntrada(BaseModel):
    nombre_usuario: str = Field(min_length=3, max_length=50)
    correo: str = Field(min_length=5, max_length=120)
    contrasena: str = Field(min_length=6, max_length=72)
    ciudad: str | None = None
    telefono: str | None = None


class LoginEntrada(BaseModel):
    nombre_usuario: str
    contrasena: str


class UsuarioSalida(BaseModel):
    id: int
    nombre_usuario: str
    correo: str
    ciudad: str | None = None
    telefono: str | None = None

    model_config = {"from_attributes": True}


class UsuarioEdicion(BaseModel):
    """Todos opcionales: solo se cambia lo que se envie. La contrasena pide la actual."""
    nombre_usuario: str | None = Field(default=None, min_length=3, max_length=50)
    correo: str | None = Field(default=None, min_length=5, max_length=120)
    ciudad: str | None = None
    telefono: str | None = None
    contrasena_actual: str | None = None
    contrasena_nueva: str | None = Field(default=None, min_length=6, max_length=72)


class TokenSalida(BaseModel):
    token: str
    usuario: UsuarioSalida

class ImagenSalida(BaseModel):
    id: int
    archivo: str
    es_principal: bool

    model_config = {"from_attributes": True}


class VehiculoEntrada(BaseModel):
    marca: str = Field(min_length=2, max_length=50)
    modelo: str = Field(min_length=1, max_length=80)
    anio: int = Field(ge=1900, le=2100)
    color: str = Field(min_length=2, max_length=30)
    kilometraje: int = Field(ge=0)
    precio: float = Field(gt=0)
    descripcion: str = ""
    ciudad: str | None = None


class VehiculoEdicion(BaseModel):
    """Todos los campos son opcionales: solo se cambia lo que se envie."""
    marca: str | None = Field(default=None, min_length=2, max_length=50)
    modelo: str | None = Field(default=None, min_length=1, max_length=80)
    anio: int | None = Field(default=None, ge=1900, le=2100)
    color: str | None = Field(default=None, min_length=2, max_length=30)
    kilometraje: int | None = Field(default=None, ge=0)
    precio: float | None = Field(default=None, gt=0)
    descripcion: str | None = None
    ciudad: str | None = None
    estado: str | None = None


class VehiculoSalida(BaseModel):
    id: int
    vendedor_id: int
    marca: str
    modelo: str
    anio: int
    color: str
    kilometraje: int
    precio: float
    descripcion: str
    ciudad: str | None = None
    estado: str
    imagenes: list[ImagenSalida] = []

    model_config = {"from_attributes": True}


class ContactoSalida(BaseModel):
    nombre_usuario: str
    correo: str
    telefono: str | None = None
    ciudad: str | None = None

    model_config = {"from_attributes": True}