import httpx
from fastapi import HTTPException
from monday_report.models.weather import WeatherDay
from monday_report.core.config import settings

class WeatherService:
    BASE_URL = "https://api.open-meteo.com/v1/forecast"

    @staticmethod
    async def get_week_weather():
        params = {
            "latitude": settings.latitude,
            "longitude": settings.longitude,
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,windspeed_10m_max",
            "timezone": settings.timezone,
            "forecast_days": 7
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(WeatherService.BASE_URL, params=params, timeout=10)
                response.raise_for_status()
                data = response.json()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erreur météo : {e}")

        daily = data.get("daily", {})
        return [
            WeatherDay(
                date=date,
                temp_min=daily["temperature_2m_min"][i],
                temp_max=daily["temperature_2m_max"][i],
                precipitation=daily["precipitation_sum"][i],
                wind_max=daily["windspeed_10m_max"][i]
            )
            for i, date in enumerate(daily["time"])
        ]
