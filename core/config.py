from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str
    db_echo: str
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    
    

    @property
    def DATABASE_URI(self):
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def DB_ECHO(self):
        if self.db_echo == 1:
            return True
        else:
            return False

    @property
    def MONGODB_URI(self):
        return "mongodb://localhost:27017"

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
