# Fintech MFA API

Este es un proyecto backend de prueba para la empresa [Creze](https://creze.com/), para la posición de desarrollador fullstack.

## Descripción

El objetivo principal de este proyecto es crear una aplicación web que permita a los usuarios registrarse, iniciar sesión utilizando MFA (Multi-Factor Authentication) y ver su perfil. Orientando principalmente a la seguridad de los datos de los usuarios.

Para el backend se utilizó FastApi Docker y Postgres

## Pre requisitos

- Docker 27.3.1
- Python 3.12
- UV 0.5.0

## Tecnologías

- [FastAPI](https://fastapi.tiangolo.com/): Framework web asíncrono basado en Python 3.6+.
- [Docker](https://www.docker.com/): Plataforma de código abierto para automatizar la implementación de aplicaciones en contenedores.
- [PostgreSQL](https://www.postgresql.org/): Sistema de gestión de bases de datos relacional de código abierto.
- [SQLAlchemy](https://www.sqlalchemy.org/): Biblioteca SQL de Python que proporciona herramientas de mapeo objeto-relacional.
- [Pydantic](https://pydantic-docs.helpmanual.io/): Biblioteca para la validación de datos en Python.
- [Passlib](https://passlib.readthedocs.io/en/stable/): Biblioteca para el almacenamiento seguro de contraseñas.
- [PyJWT](https://pyjwt.readthedocs.io/en/stable/): Implementación de JSON Web Tokens (JWT) para Python.
- [PyOTP](https://pyotp.readthedocs.io/en/latest/): Implementación de TOTP (Time-based One-Time Password) para Python.
- [Boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html): SDK de AWS para Python.
- [SlowAPI](https://slowapi.tiangolo.com/): Extensión de FastAPI para limitar la velocidad de las solicitudes.
- [Alembic](https://alembic.sqlalchemy.org/en/latest/): Herramienta de migración de bases de datos para SQLAlchemy.
- [artillery](https://artillery.io/): Herramienta de prueba de carga y rendimiento.

## Instalación

1. Clonar el repositorio

```bash
git clone https://github.com/UrielCuriel/fintech-mfa-api.git
```

2. Crear un archivo `.env` en la raíz del proyecto, se puede utilizar el archivo `.env.example` como referencia. la documentación de las variables de entorno se encuentra en la sección de [Variables de entorno](#variables-de-entorno)

3. Ejecutar el siguiente comando para correr el proyecto

```bash
docker compose watch
```

## Estructura del Proyecto

```
fintech-mfa-api/
├── app/
│   ├── api/
│   │   ├── routes/
│   │   │   ├── auth.py      # Rutas de autenticación
│   │   │   ├── login.py     # Rutas de inicio de sesión
│   │   │   └── users.py     # Rutas de usuarios
│   │   ├── deps.py          # Dependencias de la API
│   │   └── main.py          # Configuración principal de la API
│   ├── core/
│   │   ├── config.py        # Configuraciones generales
│   │   ├── db.py           # Configuración de base de datos
│   │   └── security.py     # Configuraciones de seguridad
│   ├── crud.py             # Operaciones CRUD
│   ├── models.py           # Modelos de la base de datos
│   ├── schemas.py          # Esquemas Pydantic
│   ├── utils.py            # Utilidades generales
│   ├── mails.py            # Funcionalidades de correo
│   ├── main.py             # Punto de entrada de la aplicación
│   ├── initial_data.py     # Datos iniciales
│   └── backend_pre_start.py # Scripts de pre-inicio
└── tests/                  # Tests unitarios y de integración
```

## Base de Datos

Este proyecto utiliza PostgreSQL como base de datos. La configuración de la base de datos se encuentra en el archivo `app/core/db.py`.

Para crear la base de datos, ejecuta el siguiente comando:

```bash
docker compose exec api alembic upgrade head
```

## API Endpoints

La API proporciona los siguientes endpoints principales:

- `/api/v1/login/`: Endpoints de autenticación

  - `POST /access-token/`: Obtener token de acceso
  - `POST /access-token/otp/`: Verificar OTP y obtener token de acceso

- `/api/v1/users/`: Endpoints de usuarios

  - `GET /me`: Obtener perfil del usuario actual
  - `PATCH /me`: Actualizar perfil del usuario actual
  - `POST /register/`: Registrar un nuevo usuario

- `/api/v1/auth/`: Endpoints de autenticación
  - `PUT /otp/enable/`: Habilitar autenticación de dos factores
  - `PUT /otp/generate/`: Generar qr code para autenticación de dos factores

Para más detalles, consulta la documentación interactiva en `/docs` o visitando la documentación más detallada en [fintech Docs](https://fintech-docs.urielcuriel.com/)

## Tests

Para ejecutar los tests:

```bash
# Ejecutar todos los tests
uv run pytest tests/
```

Para tests de rendimiento:

```bash
# Ejecutar tests de rendimiento
npx artillery run tests/rate-limit-test.yml
```

## Variables de entorno

[Mantener la sección existente de variables de entorno...]

## Seguridad

Este proyecto implementa las siguientes medidas de seguridad:

- Autenticación de dos factores (2FA/MFA)
- Tokens JWT para manejo de sesiones
- Rate limiting para prevenir ataques de fuerza bruta
- Almacenamiento seguro de contraseñas con hash y salt
- Validación de datos con Pydantic
- CORS configurables para control de acceso