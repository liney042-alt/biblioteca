# Importo las herramientas de FastAPI y SQLite
from fastapi import APIRouter, HTTPException, status, Depends
import sqlite3

# Importo la conexión a la base de datos
from app.database import obtener_conexion

# Importo los esquemas de los libros
from app import schemas

# Importo las funciones de autenticación y permisos
from app.security import obtener_usuario_actual, verificar_admin


# Organizo las rutas de los libros
router = APIRouter(
    prefix="/libros",
    tags=["Libros"]
)


# Endpoint para crear un libro
@router.post("/", status_code=status.HTTP_201_CREATED)
def crear_libro(
    libro: schemas.Libro,
    usuario_actual: dict = Depends(verificar_admin)
):
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    # Inserto el nuevo libro en la tabla libros
    cursor.execute("""
        INSERT INTO libros (
            titulo,
            autor,
            año_publicacion,
            descripcion
        )
        VALUES (?, ?, ?, ?)
    """, (
        libro.titulo,
        libro.autor,
        libro.año_publicacion,
        libro.descripcion
    ))

    conexion.commit()

    # Obtengo el ID generado para el libro
    libro_id = cursor.lastrowid

    conexion.close()

    return {
        "mensaje": "Libro creado correctamente",
        "id": libro_id,
        "titulo": libro.titulo,
        "autor": libro.autor,
        "año_publicacion": libro.año_publicacion,
        "descripcion": libro.descripcion
    }


# Endpoint para listar todos los libros
@router.get("/")
def listar_libros(
    usuario_actual: dict = Depends(obtener_usuario_actual)
):
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    # Consulto los libros y verifico si están disponibles
    cursor.execute("""
        SELECT
            l.id,
            l.titulo,
            l.autor,
            l.año_publicacion,
            l.descripcion,
            CASE
                WHEN EXISTS (
                    SELECT 1
                    FROM prestamos p
                    WHERE p.libro_id = l.id
                    AND p.estado = 'activo'
                )
                THEN 0
                ELSE 1
            END AS disponible
        FROM libros l
    """)

    libros = cursor.fetchall()

    conexion.close()

    # Creo una lista para organizar la respuesta
    resultado = []

    # Recorro cada libro encontrado
    for libro in libros:
        resultado.append({
            "id": libro["id"],
            "titulo": libro["titulo"],
            "autor": libro["autor"],
            "año_publicacion": libro["año_publicacion"],
            "descripcion": libro["descripcion"],

            # Convierto el valor 0 o 1 en False o True
            "disponible": bool(libro["disponible"])
        })

    return resultado


# Endpoint para consultar un libro por su ID
# Requiere un usuario autenticado
@router.get("/{libro_id}")
def obtener_libro(
    libro_id: int,
    usuario_actual: dict = Depends(obtener_usuario_actual)
):
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    # Busco el libro por su ID y verifico su disponibilidad
    cursor.execute("""
        SELECT
            l.id,
            l.titulo,
            l.autor,
            l.año_publicacion,
            l.descripcion,
            CASE
                WHEN EXISTS (
                    SELECT 1
                    FROM prestamos p
                    WHERE p.libro_id = l.id
                    AND p.estado = 'activo'
                )
                THEN 0
                ELSE 1
            END AS disponible
        FROM libros l
        WHERE l.id = ?
    """, (libro_id,))

    libro = cursor.fetchone()

    conexion.close()

    # Si el libro no existe, devuelvo un error 404
    if libro is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Libro no encontrado"
        )

    return {
        "id": libro["id"],
        "titulo": libro["titulo"],
        "autor": libro["autor"],
        "año_publicacion": libro["año_publicacion"],
        "descripcion": libro["descripcion"],
        "disponible": bool(libro["disponible"])
    }


# Endpoint para actualizar un libro
# Solo puede acceder un administrador
@router.put("/{libro_id}")
def actualizar_libro(
    libro_id: int,
    libro: schemas.Libro,
    usuario_actual: dict = Depends(verificar_admin)
):
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    # Verifico que el libro exista
    cursor.execute("""
        SELECT * FROM libros
        WHERE id = ?
    """, (libro_id,))

    libro_existente = cursor.fetchone()

    # Si no existe, devuelvo un error 404
    if libro_existente is None:
        conexion.close()

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Libro no encontrado"
        )

    # Actualizo los datos del libro
    cursor.execute("""
        UPDATE libros
        SET titulo = ?,
            autor = ?,
            año_publicacion = ?,
            descripcion = ?
        WHERE id = ?
    """, (
        libro.titulo,
        libro.autor,
        libro.año_publicacion,
        libro.descripcion,
        libro_id
    ))

    conexion.commit()

    conexion.close()

    return {
        "mensaje": "Libro actualizado correctamente",
        "id": libro_id,
        "titulo": libro.titulo,
        "autor": libro.autor,
        "año_publicacion": libro.año_publicacion,
        "descripcion": libro.descripcion
    }


# Endpoint para eliminar un libro
# Solo puede acceder un administrador
@router.delete("/{libro_id}")
def eliminar_libro(
    libro_id: int,
    usuario_actual: dict = Depends(verificar_admin)
):
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    # Verifico que el libro exista
    cursor.execute("""
        SELECT * FROM libros
        WHERE id = ?
    """, (libro_id,))

    libro = cursor.fetchone()

    # Si no existe, devuelvo un error 404
    if libro is None:
        conexion.close()

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Libro no encontrado"
        )

    try:
        # Intento eliminar el libro
        cursor.execute("""
            DELETE FROM libros
            WHERE id = ?
        """, (libro_id,))

        conexion.commit()

    # Controlo el error si el libro tiene préstamos registrados
    except sqlite3.IntegrityError:
        conexion.close()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No se puede eliminar el libro porque tiene préstamos registrados"
        )

    conexion.close()

    return {
        "mensaje": "Libro eliminado correctamente",
        "id": libro_id
    }


# Endpoint para consultar un libro junto con sus préstamos
# Requiere un usuario autenticado
@router.get("/{libro_id}/prestamos")
def obtener_libro_con_prestamos(
    libro_id: int,
    usuario_actual: dict = Depends(obtener_usuario_actual)
):
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    # Busco el libro por su ID
    cursor.execute("""
        SELECT *
        FROM libros
        WHERE id = ?
    """, (libro_id,))

    libro = cursor.fetchone()

    # Si no existe, devuelvo un error 404
    if libro is None:
        conexion.close()

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Libro no encontrado"
        )

    # Busco los préstamos relacionados con el libro
    cursor.execute("""
        SELECT *
        FROM prestamos
        WHERE libro_id = ?
    """, (libro_id,))

    # Obtengo todos los préstamos encontrados
    prestamos = cursor.fetchall()

    conexion.close()

    # Creo una lista para organizar los préstamos
    lista_prestamos = []

    # Recorro cada préstamo
    for prestamo in prestamos:
        lista_prestamos.append({
            "id": prestamo["id"],
            "usuario": prestamo["usuario"],
            "dias_prestamo": prestamo["dias_prestamo"],
            "estado": prestamo["estado"]
        })

    # Devuelvo los datos del libro y sus préstamos
    return {
        "id": libro["id"],
        "titulo": libro["titulo"],
        "autor": libro["autor"],
        "año_publicacion": libro["año_publicacion"],
        "descripcion": libro["descripcion"],
        "prestamos": lista_prestamos
    }