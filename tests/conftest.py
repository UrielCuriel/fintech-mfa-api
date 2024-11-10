import pytest

from dotenv import load_dotenv
from sqlmodel import Session, create_engine, SQLModel
from app.models import User

load_dotenv(".env.test", override=True)
from app.core.config import settings
# Fixture para crear el motor de la base de datos
@pytest.fixture(scope="session")
def engine():
    """Crear un motor de base de datos para pruebas y eliminarlo al finalizar."""
    # Crear un motor para la base de datos de prueba
    test_engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))
    # Crear todas las tablas antes de ejecutar las pruebas
    SQLModel.metadata.create_all(test_engine)
    yield test_engine
    # Eliminar todas las tablas al finalizar las pruebas
    SQLModel.metadata.drop_all(test_engine)
    test_engine.dispose()

# Fixture para crear una sesión de base de datos
@pytest.fixture(scope="function")
def session(engine):
    """Proporcionar una sesión de base de datos para cada prueba."""
    # Crear una sesión de base de datos
    session = Session(engine)
    
    # Limpiar la base de datos antes de cada prueba
    _clear_db(session)
    
    # Devolver la sesión
    yield session
    
    # Cerrar la sesión después de cada prueba
    session.close()

def _clear_db(session):
    """Limpiar la base de datos antes de cada prueba."""
    # Borrar todos los registros de las tablas
    for table in reversed(SQLModel.metadata.sorted_tables):
        session.execute(table.delete())
    
    # Confirmar los cambios
    session.commit()


@pytest.fixture
def current_user() -> User:
    """
    Fixture to create an authenticated user for testing.

    Returns:
        User: An instance of the User model with the username "testuser" and email "test@example.com".
    """
    # Tu lógica para crear un usuario autenticado
    return User(username="testuser", email="test@example.com")

