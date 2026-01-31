from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    DATABASE_URL: str

    OPENAI_API_KEY: str | None = None

    class Config:
        env_file = ".env"

settings = Settings()
