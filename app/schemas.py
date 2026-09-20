
from pydantic import BaseModel
from typing import Optional


class Libro(BaseModel):
    titulo: str
    autor: str
    año_publicacion: int
    descripcion: Optional[str] = None


class PrestamoCrear(BaseModel):
    libro_id: int
    dias_prestamo: int


class UsuarioCrear(BaseModel):
    username: str
    password: str


class UsuarioLogin(BaseModel):
    username: str
    password: str