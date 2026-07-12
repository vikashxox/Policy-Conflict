import os
from typing import Any


class Settings:
    def __init__(self) -> None:
        self.project_name: str = os.getenv("PROJECT_NAME", "Policy Guardian API")
        self.api_v1_prefix: str = os.getenv("API_V1_PREFIX", "/api")
        self.debug: bool = os.getenv("DEBUG", "false").lower() in {"1", "true", "yes", "on"}
        self.database_url: str = os.getenv(
            "DATABASE_URL",
            "postgresql+psycopg2://postgres:postgres@localhost:5432/policy_guardian",
        )
        if self.database_url.startswith("postgresql") and os.getenv("USE_SQLITE_FALLBACK", "1") == "1":
            self.database_url = "sqlite:///backend/app/database/policy_guardian.db"
        self.secret_key: str = os.getenv("SECRET_KEY", "policy-guardian-dev-secret")
        self.algorithm: str = os.getenv("ALGORITHM", "HS256")
        self.access_token_expire_minutes: int = int(
            os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "480")
        )
        self.cors_origins: list[str] = [
            origin.strip()
            for origin in os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",")
            if origin.strip()
        ]
        self.log_level: str = os.getenv("LOG_LEVEL", "INFO")
        self.log_format: str = os.getenv("LOG_FORMAT", "%(asctime)s %(levelname)s %(name)s %(message)s")
        self.grc_dataset_path: str = os.getenv(
            "GRC_DATASET_PATH",
            "D:/Downloads/GRC-Hackathon-main/Problem Statements/Problem_11_Policy_Conflict/sample_data/problem_11",
        )


settings = Settings()


def get_settings() -> Settings:
    return settings
