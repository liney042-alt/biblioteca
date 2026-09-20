import sqlite3
from app.security import encriptar_password


def obtener_conexion():
    """
    Crea y retorna una conexión a la base de datos SQLite.
    Configura row_factory para acceder a las columnas por nombre y activa claves foráneas.
    """
    conexion = sqlite3.connect("biblioteca.db")
    conexion.row_factory = sqlite3.Row
    conexion.execute("PRAGMA foreign_keys = ON")
    return conexion


def inicializar_bd():
    """
    Crea las tablas necesarias si no existen y realiza migraciones sencillas.
    """
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    # 1. Crear tabla de usuarios
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            rol TEXT NOT NULL DEFAULT 'usuario'
        )
    """)

    # 2. Crear tabla de libros
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS libros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            autor TEXT NOT NULL,
            año_publicacion INTEGER NOT NULL,
            descripcion TEXT
        )
    """)

    # 3. Crear tabla de préstamos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS prestamos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            libro_id INTEGER NOT NULL,
            usuario TEXT NOT NULL,
            dias_prestamo INTEGER NOT NULL,
            estado TEXT NOT NULL DEFAULT 'activo',
            FOREIGN KEY (libro_id) REFERENCES libros (id)
        )
    """)

    # 4. Comprobar si la columna estado existe
    cursor.execute("PRAGMA table_info(prestamos)")
    columnas = [columna["name"] for columna in cursor.fetchall()]

    if "estado" not in columnas:
        cursor.execute("""
            ALTER TABLE prestamos
            ADD COLUMN estado TEXT NOT NULL DEFAULT 'activo'
        """)

    conexion.commit()
    conexion.close()


def crear_admin_inicial():
    """
    Crea el usuario administrador por defecto si aún no existe.
    """
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute(
        "SELECT id FROM usuarios WHERE username = ?",
        ("admin",)
    )

    admin_existente = cursor.fetchone()

    if not admin_existente:
        password_hash = encriptar_password("admin123")

        cursor.execute("""
            INSERT INTO usuarios (username, password, rol)
            VALUES (?, ?, ?)
        """, ("admin", password_hash, "admin"))

        conexion.commit()

    conexion.close()