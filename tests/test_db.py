from sqlmodel import select
from app.core.db import init_db

from app.models import User
from app.schemas import UserCreate
from app import crud

from app.core.config import settings


def test_init_db(session):
    # Asegurarse de que la base de datos esté vacía al inicio
    users = session.exec(select(User)).all()
    assert len(users) == 0

    # Inicializar la base de datos
    init_db(session)

    # Verificar si se creó el superusuario
    user = session.exec(select(User).where(User.email == settings.FIRST_SUPERUSER)).first()
    assert user is not None
    assert user.email == settings.FIRST_SUPERUSER
    assert user.is_superuser is True

def test_init_db_existing_user(session):
    # Crear un usuario manualmente
    user_in = UserCreate(
        email=settings.FIRST_SUPERUSER,
        username=settings.FIRST_SUPERUSER,
        password=settings.FIRST_SUPERUSER_PASSWORD,
        is_superuser=True,
    )
    
    crud.create_user(session=session, user_create=user_in)

    # Inicializar la base de datos
    init_db(session)
    
    # Asegurarse de que no se creó un usuario duplicado
    users = session.exec(select(User).where(User.email == settings.FIRST_SUPERUSER)).all()
    assert len(users) == 1