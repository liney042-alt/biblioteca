from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.database import inicializar_bd, crear_admin_inicial
from app.routers import libros, prestamos, usuarios


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Se ejecuta obligatoriamente al arrancar el servidor
    inicializar_bd()
    crear_admin_inicial()
    yield
    # Código de limpieza si fuera necesario (opcional)


app = FastAPI(
    title="Biblioteca API",
    description="API para gestionar libros y préstamos",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(usuarios.router)
app.include_router(libros.router)
app.include_router(prestamos.router)


@app.get("/")
def root():
    return {"mensaje": "API de Biblioteca"}