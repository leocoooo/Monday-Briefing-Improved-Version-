from pydantic import BaseModel
from datetime import datetime

class WeatherDay(BaseModel):
    date: str
    temp_min: float | None = None
    temp_max: float | None = None
    precipitation: float = 0.0
    wind_max: float = 0.0

    def is_good_for_running(self) -> bool:
        if self.temp_max is None:
            return False
        return self.precipitation < 0.4 and self.wind_max < 20

    def to_string(self) -> str:
        try:
            date_obj = datetime.strptime(self.date, '%Y-%m-%d')
            date_fr = date_obj.strftime('%A %d %B %Y').capitalize()
        except Exception:
            date_fr = self.date
        return (f"  • {date_fr} : {self.temp_min}°C–{self.temp_max}°C, "
                f"précip. {self.precipitation}mm, vent max {self.wind_max} km/h")
