# Importo las librerías para proteger contraseñas y crear tokens
import bcrypt
import jwt

# Importo las herramientas de FastAPI para manejar seguridad y errores
from fastapi import HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends


# Clave y algoritmo utilizados para firmar los tokens JWT
SECRET_KEY = "clave-secreta-biblioteca"
ALGORITHM = "HS256"

# Configuro la autenticación mediante el esquema Bearer
security_scheme = HTTPBearer()


# Encripta la contraseña antes de guardarla en la base de datos
def encriptar_password(password: str):
    password_bytes = password.encode("utf-8")

    salt = bcrypt.gensalt()

    password_hash = bcrypt.hashpw(
        password_bytes,
        salt
    )

    return password_hash.decode("utf-8")


# Comprueba si la contraseña ingresada coincide con el hash guardado
def verificar_password(password: str, password_hash: str):
    password_bytes = password.encode("utf-8")
    hash_bytes = password_hash.encode("utf-8")

    return bcrypt.checkpw(
        password_bytes,
        hash_bytes
    )


# Crea un token JWT con el usuario y su rol
def crear_token(username: str, rol: str):
    datos = {
        "username": username,
        "rol": rol
    }

    token = jwt.encode(
        datos,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return token


# Obtiene y valida el token del usuario autenticado
def obtener_usuario_actual(
    credenciales: HTTPAuthorizationCredentials = Depends(security_scheme)
):
    token = credenciales.credentials

    try:
        datos = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        return datos

    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado"
        )


# Comprueba que el usuario tenga permisos de administrador
def verificar_admin(
    usuario_actual: dict = Depends(obtener_usuario_actual)
):
    if usuario_actual["rol"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requiere rol administrador"
        )

    return usuario_actual