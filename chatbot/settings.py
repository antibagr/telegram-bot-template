from pathlib import Path

from pydantic import BaseSettings


class Settings(BaseSettings):

    DEBUG: bool

    BASE_DIR: Path = Path(__file__).resolve().parent

    BOT_TOKEN: str
    BOT_USERNAME: str

    # pass user_id of a user who have
    # the administrator priviledges
    ADMIN_ID: int = 0

    # pass the chat_id of a chat
    # where all exceptions will be sent
    ERROR_CHAT_ID: int = 0

    PG_HOST: str = ''
    PG_USER: str = ''
    PG_PASSWORD: str = ''
    PG_DATABASE: str = ''
    PG_PORT: int = 5432

    REDIS_HOST: str = ''
    REDIS_PORT: int = 6937

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


settings = Settings()
