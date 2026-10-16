from functools import lru_cache
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "development"
    app_name: str = "UPS Digital Maturity Observatory"
    database_url: str = "sqlite:///./ups_observatory.db"
    local_database_url: str = "sqlite:///./ups_observatory.db"

    # Analytical model
    lambda_igmd: float = 0.50
    lambda_ioc: float = 0.30
    lambda_iko: float = 0.20
    dimension_weights: str = "0.20,0.20,0.20,0.20,0.20"
    objective_weights: str = "0.20,0.20,0.20,0.20,0.20"

    # Optional Notion synchronization
    notion_api_token: str = ""
    notion_root_page_id: str = "175b0841d99482f0a2a881a9c73be108"
    notion_version: str = "2022-06-28"

    # Web/authentication
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"
    initial_admin_email: str = "transformaciondigital@ups.edu.ec"
    initial_admin_name: str = "Coordinación de Transformación Digital"
    initial_admin_password: str = ""
    session_days: int = 7
    session_cookie_secure: bool = False

    # Evidence repository
    upload_dir: str = "/data/uploads"
    max_upload_mb: int = 20
    allowed_upload_extensions: str = ".pdf,.doc,.docx,.xls,.xlsx,.ppt,.pptx,.png,.jpg,.jpeg,.webp,.csv,.txt,.zip"

    @field_validator("lambda_igmd", "lambda_ioc", "lambda_iko")
    @classmethod
    def validate_lambda(cls, value: float) -> float:
        if not 0 <= value <= 1:
            raise ValueError("Layer weights must be between 0 and 1")
        return value

    @field_validator("session_days")
    @classmethod
    def validate_session_days(cls, value: int) -> int:
        if value < 1 or value > 90:
            raise ValueError("SESSION_DAYS must be between 1 and 90")
        return value

    @field_validator("max_upload_mb")
    @classmethod
    def validate_upload_size(cls, value: int) -> int:
        if value < 1 or value > 200:
            raise ValueError("MAX_UPLOAD_MB must be between 1 and 200")
        return value

    @property
    def layer_weights(self) -> tuple[float, float, float]:
        values = (self.lambda_igmd, self.lambda_ioc, self.lambda_iko)
        if abs(sum(values) - 1.0) > 1e-6:
            raise ValueError("LAMBDA_IGMD + LAMBDA_IOC + LAMBDA_IKO must equal 1")
        return values

    @staticmethod
    def _parse_weights(raw: str) -> list[float]:
        values = [float(v.strip()) for v in raw.split(",") if v.strip()]
        if len(values) != 5 or abs(sum(values) - 1.0) > 1e-6:
            raise ValueError("Expected five weights that sum to 1")
        return values

    @property
    def dimension_weight_values(self) -> list[float]:
        return self._parse_weights(self.dimension_weights)

    @property
    def objective_weight_values(self) -> list[float]:
        return self._parse_weights(self.objective_weights)

    @property
    def allowed_origins(self) -> list[str]:
        return [v.strip() for v in self.cors_origins.split(",") if v.strip()]

    @property
    def allowed_extensions(self) -> set[str]:
        return {v.strip().lower() for v in self.allowed_upload_extensions.split(",") if v.strip()}


@lru_cache
def get_settings() -> Settings:
    return Settings()
