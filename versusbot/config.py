from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    log_level: int = 10