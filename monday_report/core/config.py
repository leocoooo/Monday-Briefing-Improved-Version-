from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional, List

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
