from pydantic import BaseSettings


class Settings(BaseSettings):
    SUPABASE_URL: str = ""
    SUPABASE_SERVICE_KEY: str = ""
    DEDALUS_API_BASE: str = ""
    DEDALUS_API_KEY: str = ""
    ANTHROPIC_MODEL: str = "claude-3-7-sonnet"
    XAI_MODEL: str = "grok-2-latest"

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()  # type: ignore


