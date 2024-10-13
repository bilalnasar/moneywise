from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PLAID_CLIENT_ID: str
    PLAID_SECRET: str
    PLAID_ENV: str

    class Config:
        env_file = ".env"

settings = Settings()