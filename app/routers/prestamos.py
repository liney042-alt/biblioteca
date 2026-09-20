# Importo las herramientas de FastAPI y las dependencias de seguridad
from fastapi import APIRouter, HTTPException, status, Depends
from app.database import obtener_conexion
from app import schemas
from app.security import obtener_usuario_actual, verificar_admin


# Organizo las rutas de préstamos
router = APIRouter(
    prefix="/prestamos",
    tags=["Préstamos"]
)


# Endpoint para crear un préstamo
@router.post("/", status_code=status.HTTP_201_CREATED)
def crear_prestamo(
    prestamo: schemas.PrestamoCrear,
    usuario_actual: dict = Depends(obtener_usuario_actual)
):
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT * FROM libros
        WHERE id = ?
    """, (prestamo.libro_id,))

    libro = cursor.fetchone()

    if libro is None:
        conexion.close()

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Libro no encontrado"
        )

    # Compruebo si el libro tiene un préstamo activo
    cursor.execute("""
        SELECT * FROM prestamos
        WHERE libro_id = ?
        AND estado = 'activo'
    """, (prestamo.libro_id,))

    prestamo_activo = cursor.fetchone()

    # Evito prestar un libro que ya está prestado
    if prestamo_activo is not None:
        conexion.close()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El libro no está disponible"
        )

    # Obtengo el nombre del usuario autenticado
    username = usuario_actual["username"]

    # Registro el préstamo con estado activo
    cursor.execute("""
        INSERT INTO prestamos (
            libro_id,
            usuario,
            dias_prestamo,
            estado
        )
        VALUES (?, ?, ?, ?)
    """, (
        prestamo.libro_id,
        username,
        prestamo.dias_prestamo,
        "activo"
    ))

    # Guardo los cambios en la base de datos
    conexion.commit()

    # Obtengo el identificador del préstamo creado
    prestamo_id = cursor.lastrowid

    conexion.close()

    return {
        "mensaje": "Préstamo creado correctamente",
        "id": prestamo_id,
        "libro_id": prestamo.libro_id,
        "usuario": username,
        "dias_prestamo": prestamo.dias_prestamo,
        "estado": "activo"
    }


# Endpoint para consultar todos los préstamos
@router.get("/")
def listar_prestamos(
    usuario_actual: dict = Depends(verificar_admin)
):
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT *
        FROM prestamos
    """)

    prestamos = cursor.fetchall()

    conexion.close()

    resultado = []

    for prestamo in prestamos:
        resultado.append({
            "id": prestamo["id"],
            "libro_id": prestamo["libro_id"],
            "usuario": prestamo["usuario"],
            "dias_prestamo": prestamo["dias_prestamo"],
            "estado": prestamo["estado"]
        })

    return resultado


# Endpoint para consultar los préstamos del usuario autenticado
@router.get("/mis-prestamos")
def listar_mis_prestamos(
    usuario_actual: dict = Depends(obtener_usuario_actual)
):
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    username = usuario_actual["username"]

    cursor.execute("""
        SELECT *
        FROM prestamos
        WHERE usuario = ?
    """, (username,))

    prestamos = cursor.fetchall()

    conexion.close()

    resultado = []

    for prestamo in prestamos:
        resultado.append({
            "id": prestamo["id"],
            "libro_id": prestamo["libro_id"],
            "usuario": prestamo["usuario"],
            "dias_prestamo": prestamo["dias_prestamo"],
            "estado": prestamo["estado"]
        })

    return resultado


# Endpoint para consultar un préstamo específico
@router.get("/{prestamo_id}")
def obtener_prestamo(
    prestamo_id: int,
    usuario_actual: dict = Depends(obtener_usuario_actual)
):
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT *
        FROM prestamos
        WHERE id = ?
    """, (prestamo_id,))

    prestamo = cursor.fetchone()

    conexion.close()

    # Devuelvo 404 si el préstamo no existe
    if prestamo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Préstamo no encontrado"
        )

    # Compruebo si es administrador o propietario del préstamo
    es_admin = usuario_actual.get("rol") == "admin"
    es_propietario = prestamo["usuario"] == usuario_actual["username"]

    # Rechazo el acceso si no tiene permisos
    if not es_admin and not es_propietario:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para consultar este préstamo"
        )

    return {
        "id": prestamo["id"],
        "libro_id": prestamo["libro_id"],
        "usuario": prestamo["usuario"],
        "dias_prestamo": prestamo["dias_prestamo"],
        "estado": prestamo["estado"]
    }


# Endpoint para devolver un libro
@router.patch("/{prestamo_id}/devolver")
def devolver_prestamo(
    prestamo_id: int,
    usuario_actual: dict = Depends(obtener_usuario_actual)
):
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    # Busco el préstamo por su identificador
    cursor.execute("""
        SELECT *
        FROM prestamos
        WHERE id = ?
    """, (prestamo_id,))

    prestamo = cursor.fetchone()

    # Devuelvo 404 si el préstamo no existe
    if prestamo is None:
        conexion.close()

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Préstamo no encontrado"
        )

    # Compruebo si es administrador o propietario
    es_admin = usuario_actual.get("rol") == "admin"
    es_propietario = prestamo["usuario"] == usuario_actual["username"]

    # Impido devolver préstamos de otros usuarios
    if not es_admin and not es_propietario:
        conexion.close()

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para devolver este préstamo"
        )

    # Compruebo si el préstamo ya fue devuelto
    if prestamo["estado"] == "devuelto":
        conexion.close()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El préstamo ya fue devuelto"
        )

    # Cambio el estado del préstamo a devuelto
    cursor.execute("""
        UPDATE prestamos
        SET estado = 'devuelto'
        WHERE id = ?
    """, (prestamo_id,))

    conexion.commit()

    conexion.close()

    return {
        "mensaje": "Libro devuelto correctamente",
        "id": prestamo_id,
        "estado": "devuelto"
    }