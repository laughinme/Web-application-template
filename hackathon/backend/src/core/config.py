from pathlib import Path
from pydantic import model_validator, SecretStr

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR  = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    """
    Project dependencies config
    """
    model_config = SettingsConfigDict(
        env_file=f'{BASE_DIR}/.env',
        extra='ignore'
    )
    
    # API settings
    API_PORT: int = 8080
    API_HOST: str = '0.0.0.0'
    
    # Auth Settings    
    JWT_PRIVATE_KEY: str
    JWT_PUBLIC_KEY: str
    JWT_ALGO: str = 'RS256'
    ACCESS_TTL: int = 60 * 5
    REFRESH_TTL: int = 60 * 60 * 24 * 7
    
    # Database settings
    DB_USER: str
    DB_PASSWORD: SecretStr
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    
    # Redis settings
    REDIS_HOST: str
    REDIS_PORT: int

    # Site data (url, paths)
    SITE_URL: str = ''
    
    @property
    def DB_URI(self) -> str:
        return (
            f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD.get_secret_value()}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )
