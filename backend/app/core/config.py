import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    GEMINI_API_KEY: str
    ENVIRONMENT: str = "development"
    DATABASE_URL: str = "sqlite+aiosqlite:///./claimiq.db"
    TESSERACT_CMD: str = "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
    CORS_ORIGINS: str = "http://localhost:5173"
    SUPABASE_URL: str | None = None
    SUPABASE_SERVICE_KEY: str | None = None
    
    # Resolve absolute path to data/policy_terms.json
    POLICY_TERMS_PATH: str = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "data",
        "policy_terms.json"
    )

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",")]

settings = Settings()
