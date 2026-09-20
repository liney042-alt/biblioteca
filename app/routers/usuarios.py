# Importo las herramientas de FastAPI y SQLite
from fastapi import APIRouter, HTTPException, status
import sqlite3

# Importo la conexión, los esquemas y las funciones de seguridad
from app.database import obtener_conexion
from app import schemas, security


# Organizo las rutas de usuarios
router = APIRouter(
    prefix="/usuarios",
    tags=["Usuarios"]
)


# Endpoint para registrar un nuevo usuario
@router.post("/registro", status_code=status.HTTP_201_CREATED)
def registrar_usuario(usuario: schemas.UsuarioCrear):
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    password_hash = security.encriptar_password(usuario.password)
    rol = "usuario"

    try:
        cursor.execute("""
            INSERT INTO usuarios (username, password, rol)
            VALUES (?, ?, ?)
        """, (
            usuario.username,
            password_hash,
            rol
        ))

        conexion.commit()

    # Controlo el error si el usuario ya existe
    except sqlite3.IntegrityError:
        conexion.close()
        raise HTTPException(
            status_code=400,
            detail="El usuario ya existe"
        )

    conexion.close()

    # Devuelvo la confirmación del registro
    return {
        "mensaje": "Usuario registrado correctamente",
        "username": usuario.username,
        "rol": rol
    }


# Endpoint para iniciar sesión
@router.post("/login")
def iniciar_sesion(usuario: schemas.UsuarioLogin):

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT * FROM usuarios
        WHERE username = ?
    """, (usuario.username,))

    usuario_db = cursor.fetchone()
    conexion.close()

    if usuario_db is None:
        raise HTTPException(
            status_code=401,
            detail="Usuario o contraseña incorrectos"
        )

    password_correcta = security.verificar_password(
        usuario.password,
        usuario_db["password"]
    )

    # Rechazo las credenciales incorrectas
    if not password_correcta:
        raise HTTPException(
            status_code=401,
            detail="Usuario o contraseña incorrectos"
        )

    # Creo un token JWT con el usuario y su rol
    token = security.crear_token(
        usuario_db["username"],
        usuario_db["rol"]
    )

    return {
        "mensaje": "Inicio de sesión exitoso",
        "access_token": token,
        "token_type": "bearer"
    }