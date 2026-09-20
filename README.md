
# Biblioteca API

API REST desarrollada con FastAPI para gestionar libros, usuarios y préstamos de una biblioteca.

## Desarrolada por: 

-Liney Ricardo Medina

## Tecnologías utilizadas

- Python
- FastAPI
- Uvicorn
- Pydantic
- SQLite
- bcrypt
- PyJWT

## Estructura del proyecto

```text
R1/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── database.py
│   ├── schemas.py
│   ├── security.py
│   └── routers/
│       ├── __init__.py
│       ├── libros.py
│       ├── prestamos.py
│       └── usuarios.py
├── .gitignore
├── README.md
└── requirements.txt
```

## Instalación

### 1. Crear el entorno virtual

```bash
python -m venv venv
```

### 2. Activar el entorno virtual en Windows

En PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

### 3. Instalar las dependencias

```bash
pip install -r requirements.txt
```

## Ejecución

Iniciar la API con Uvicorn:

```bash
uvicorn app.main:app --reload
```

La API estará disponible en:

```text
http://127.0.0.1:8000
```

Documentación interactiva:

```text
http://127.0.0.1:8000/docs
```

## Funcionalidades

### Libros

- Crear un libro.
- Consultar todos los libros.
- Consultar un libro por su ID.
- Actualizar un libro.
- Eliminar un libro.
- Consultar un libro junto con sus préstamos.

### Usuarios

- Registrar usuarios.
- Iniciar sesión.
- Autenticación mediante JWT.
- Contraseñas protegidas con bcrypt.

### Préstamos

- Crear un préstamo.
- Consultar los préstamos.
- Consultar los préstamos del usuario autenticado.
- Consultar un préstamo específico.
- Devolver un libro.
- Verificar la disponibilidad de los libros.

## Seguridad y permisos

- Los endpoints protegidos requieren un token JWT.
- Las operaciones de escritura de libros requieren rol de administrador.
- La eliminación de libros está reservada al administrador.
- Los usuarios normales no pueden realizar operaciones reservadas al administrador.

## Usuario administrador inicial

Al iniciar la aplicación se crea un administrador inicial si todavía no existe:

```text
Usuario: admin
Contraseña: admin123
```

Para acceder a los endpoints protegidos:

1. Iniciar sesión mediante `/usuarios/login`.
2. Copiar el token recibido.
3. Pulsar el botón `Authorize` en la documentación de Swagger.
4. Introducir el token con el esquema Bearer.

## Base de datos

La aplicación utiliza SQLite para almacenar:

- Libros.
- Usuarios.
- Préstamos.

Las relaciones entre las tablas se gestionan mediante claves foráneas.

## Endpoints principales

| Método | Endpoint | Descripción |
|---|---|---|
| POST | `/usuarios/registro` | Registrar usuario |
| POST | `/usuarios/login` | Iniciar sesión |
| GET | `/libros/` | Listar libros |
| GET | `/libros/{libro_id}` | Consultar libro |
| POST | `/libros/` | Crear libro |
| PUT | `/libros/{libro_id}` | Actualizar libro |
| DELETE | `/libros/{libro_id}` | Eliminar libro |
| GET | `/libros/{libro_id}/prestamos` | Consultar libro con sus préstamos |
| POST | `/prestamos/` | Crear préstamo |
| GET | `/prestamos/mis-prestamos` | Consultar mis préstamos |
| GET | `/prestamos/{prestamo_id}` | Consultar préstamo |
| PATCH | `/prestamos/{prestamo_id}/devolver` | Devolver préstamo |

