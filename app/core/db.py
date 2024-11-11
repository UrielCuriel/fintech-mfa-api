from sqlmodel import Session, create_engine, select
from app.core.config import settings
from sqlalchemy.pool import QueuePool

engine = create_engine(
    str(settings.SQLALCHEMY_DATABASE_URI),
    echo=False,
    # Configuración necesaria para evitar desconexiones en producción ya que
    # Neon cierra las conexiones después de un tiempo de inactividad
    poolclass=QueuePool,
    pool_size=5,              # Número máximo de conexiones en el pool
    max_overflow=10,          # Conexiones adicionales si el pool está lleno
    pool_timeout=30,          # Tiempo máximo para esperar una conexión libre
    pool_recycle=1800,        # Tiempo (en segundos) para reciclar conexiones y evitar desconexiones
    pool_pre_ping=True        # Verifica si la conexión es válida antes de usarla
)


# make sure all SQLModel models are imported (app.models) before initializing DB
# otherwise, SQLModel might fail to initialize relationships properly
# for more details: https://github.com/fastapi/full-stack-fastapi-template/issues/28


def init_db(session: Session) -> None:
    # Tables should be created with Alembic migrations
    # But if you don't want to use migrations, create
    # the tables un-commenting the next lines
    # from sqlmodel import SQLModel

    # This works because the models are already imported and registered from app.models
    # SQLModel.metadata.create_all(engine)

    user = session.exec(
        select(User).where(User.email == settings.FIRST_SUPERUSER)
    ).first()
    if not user:
        user_in = UserCreate(
            email=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            is_superuser=True,
        )
        user = crud.create_user(session=session, user_create=user_in)
