from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    ENV: str = "development"
    DATABASE_URL: str
    QDRANT_URL: str
    LLM_PROVIDER: str = "openai"
    OPENAI_API_KEY: str | None = None
    ANTHROPIC_API_KEY: str | None = None
    GITHUB_TOKEN: str

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()