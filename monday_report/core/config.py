from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional, List
import os

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra='ignore'
    )

    # Core parameters
    latitude: float = 48.8566
    longitude: float = 2.3522
    timezone: str = "Europe/Paris"

    # Football
    football_data_api_key: Optional[str] = None
    team_id: int = 524
    team_name: str = "Paris Saint-Germain"

    # Email 
    smtp_host: Optional[str] = None
    smtp_port: int = 587
    smtp_user: Optional[str] = None
    smtp_password: Optional[str] = None
    email_from: Optional[str] = None
    email_to: Optional[str] = None
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Charger les secrets depuis Secrets Manager si on est sur Lambda
        if os.getenv("AWS_EXECUTION_ENV"):
            self._load_secrets_from_aws()
    
    def _load_secrets_from_aws(self):
        """Charge les secrets depuis AWS Secrets Manager"""
        try:
            from monday_report.core.secrets import get_secrets
            secrets = get_secrets()
            
            # Mettre à jour les attributs avec les secrets
            if secrets:
                self.smtp_host = secrets.get("SMTP_HOST", self.smtp_host)
                self.smtp_port = int(secrets.get("SMTP_PORT", self.smtp_port))
                self.smtp_user = secrets.get("SMTP_USER", self.smtp_user)
                self.smtp_password = secrets.get("SMTP_PASSWORD", self.smtp_password)
                self.email_from = secrets.get("EMAIL_FROM", self.email_from)
                self.email_to = secrets.get("EMAIL_TO", self.email_to)
                self.football_data_api_key = secrets.get("FOOTBALL_DATA_API_KEY", self.football_data_api_key)
        except Exception as e:
            import logging
            logging.error(f"Erreur lors du chargement des secrets: {e}")

settings = Settings()


class CityFilterConfig:
    def __init__(self) -> None:
        self.min_population: int = 50000
        self.max_population: Optional[int] = None
        self.included_regions: Optional[List[str]] = None
        self.excluded_regions: Optional[List[str]] = None
        self.included_departments: Optional[List[str]] = None
        self.excluded_departments: Optional[List[str]] = None

city_filter = CityFilterConfig()
