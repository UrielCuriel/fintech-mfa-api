import secrets
import warnings
import boto3
from typing import Annotated, Any, Literal, List, Union
from pydantic import (
    AnyUrl,
    BeforeValidator,
    PostgresDsn,
    computed_field,
    model_validator,
)
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing_extensions import Self

# ---------------------------
# Funciones auxiliares
# ---------------------------

def parse_cors(v: Any) -> Union[List[str], str]:
    """
    Valida y parsea las URLs CORS.
    Convierte una cadena de texto a una lista de URLs si es necesario.
    """
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",")]
    elif isinstance(v, (List, str)):
        return v
    raise ValueError(v)

# ---------------------------
# Configuración de Settings
# ---------------------------

class Settings(BaseSettings):
    """
    Clase de configuración principal utilizando Pydantic para manejar
    los valores de configuración de la aplicación.
    """

    # ---------------------------
    # Configuración de Pydantic
    # ---------------------------
    model_config = SettingsConfigDict(
        env_ignore_empty=True,
        extra="ignore",
    )

    # ---------------------------
    # Variables de entorno relacionadas con la API
    # ---------------------------
    API_VERSION: str = None
    @property
    def API_V_STR(self) -> str:
        """Retorna la versión de la API como un string con el prefijo '/api/'"""
        return f"/api/{self.API_VERSION}"

    # ---------------------------
    # Configuración de Seguridad
    # ---------------------------
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 días de duración
    TEMP_TOKEN_EXPIRE_MINUTES: int = 5  # 5 minutos de duración
    FRONTEND_HOST: str = "http://localhost:3000"
    ENVIRONMENT: Literal["local", "staging", "production"] = "local"
    
    # ---------------------------
    # Configuración de TOTP
    # ---------------------------
    TOTP_ISSUER: str = "Fintech API"
    # ---------------------------
    # Configuración de CORS
    # ---------------------------
    BACKEND_CORS_ORIGINS: Annotated[Union[List[AnyUrl], str], BeforeValidator(parse_cors)] = []

    @computed_field
    @property
    def all_cors_origins(self) -> List[str]:
        """Devuelve todas las URLs CORS configuradas y la URL del frontend"""
        return [str(origin).rstrip("/") for origin in self.BACKEND_CORS_ORIGINS] + [self.FRONTEND_HOST]

    # ---------------------------
    # Configuración de la base de datos PostgreSQL
    # ---------------------------
    PROJECT_NAME: str
    POSTGRES_SERVER: str
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str = ""
    POSTGRES_DB: str = ""

    @computed_field
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> PostgresDsn:
        """
        Devuelve la URI de conexión a la base de datos en formato DSN.
        Utiliza las configuraciones de PostgreSQL definidas.
        """
        return MultiHostUrl.build(
            scheme="postgresql+psycopg",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_SERVER,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_DB,
        )

    # ---------------------------
    # Configuración de Usuario y Contraseña
    # ---------------------------
    FIRST_SUPERUSER: str = ""
    FIRST_SUPERUSER_EMAIL: str = ""
    FIRST_SUPERUSER_PASSWORD: str = ""

    # ---------------------------
    # Configuración de Email
    # ---------------------------
    MAILERSEND_API_KEY: str = ""
    MAILERSEND_SENDER: str = None
    SUPPORT_EMAIL: str = None
    EMAIL_RESET_TOKEN_EXPIRE_HOURS: int = 48

    # ---------------------------
    # Validación de secretos por seguridad
    # ---------------------------
    def _check_default_secret(self, var_name: str, value: Union[str, None]) -> None:
        """
        Valida que los secretos no contengan el valor predeterminado 'changethis'.
        Lanza advertencias o excepciones según el entorno.
        """
        if value == "changethis":
            message = (
                f'The value of {var_name} is "changethis", '
                "for security, please change it, at least for deployments."
            )
            if self.ENVIRONMENT == "local":
                warnings.warn(message, stacklevel=1)
            else:
                raise ValueError(message)

    @model_validator(mode="after")
    def _enforce_non_default_secrets(self) -> Self:
        """Valida que todos los secretos críticos estén configurados correctamente."""
        self._check_default_secret("SECRET_KEY", self.SECRET_KEY)
        self._check_default_secret("POSTGRES_PASSWORD", self.POSTGRES_PASSWORD)
        self._check_default_secret("FIRST_SUPERUSER_PASSWORD", self.FIRST_SUPERUSER_PASSWORD)
        self._check_default_secret("MAILERSEND_API_KEY", self.MAILERSEND_API_KEY)
        return self

    # ---------------------------
    # Configuración de AWS (si es necesario)
    # ---------------------------
    AWS_ENDPOINT_URL: str = ""
    AWS_REGION: str = "us-east-1"

    def get_secret_from_aws(self, secret_name: str) -> str:
        """
        Obtiene un secreto de AWS Secrets Manager, con soporte para LocalStack.
        """
        session = boto3.session.Session()
        client_params = {
            "service_name": "secretsmanager",
        }
        if self.AWS_ENDPOINT_URL:
            client_params["endpoint_url"] = self.AWS_ENDPOINT_URL
            client_params["region_name"] = self.AWS_REGION

        client = session.client(**client_params)

        try:
            get_secret_value_response = client.get_secret_value(SecretId=secret_name)
            return get_secret_value_response['SecretString']
        except Exception as e:
            if self.ENVIRONMENT == "local":
                warnings.warn(f"Could not fetch secret {secret_name}: {e}")
            else:
                raise ValueError(f"Could not fetch secret {secret_name}: {e}")

    # ---------------------------
    # Constructor de la clase Settings
    # ---------------------------
    def __init__(self, **kwargs):
        """
        Inicializa las configuraciones y obtiene secretos de AWS si no están configurados.
        """
        super().__init__(**kwargs)
        secrets = ["SECRET_KEY", "POSTGRES_PASSWORD", "FIRST_SUPERUSER_PASSWORD", "MAILERSEND_API_KEY"]
        for secret in secrets:
            if not getattr(self, secret):
                setattr(self, secret, self.get_secret_from_aws(f"{self.PROJECT_NAME}/{secret}"))

# ---------------------------
# Instancia global de configuración
# ---------------------------
settings = Settings()