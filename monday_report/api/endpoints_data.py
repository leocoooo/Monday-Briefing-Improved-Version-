from typing import List
from fastapi import APIRouter
from pydantic import BaseModel
from datetime import datetime

from monday_report.services.weather_service import WeatherService
from monday_report.services.football_service import FootballService
from monday_report.services.geo_service import GeoService
from monday_report.models.weather import WeatherDay

router = APIRouter(prefix="/data", tags=["data"])


class WeatherResponse(BaseModel):
    forecast: List[WeatherDay]


class RunningDaysResponse(BaseModel):
    optimal_days: List[str]
    count: int


class MatchesResponse(BaseModel):
    team_name: str
    matches: List[str]


class RandomCityResponse(BaseModel):
    city_info: str


@router.get("/weather", response_model=WeatherResponse)
async def get_weather():
    """
    Retourne les prévisions météo pour les 7 prochains jours.
    """
    weather_days = await WeatherService.get_week_weather()
    return WeatherResponse(forecast=weather_days)


@router.get("/running-days", response_model=RunningDaysResponse)
async def get_running_days():
    """
    Retourne les jours optimaux pour aller courir (précipitations < 0.4mm, vent < 20 km/h).
    """
    weather_days = await WeatherService.get_week_weather()
    running_days = []
    
    for day in weather_days:
        if day.is_good_for_running():
            date_fr = datetime.strptime(day.date, '%Y-%m-%d').strftime('%A %d %B').capitalize()
            running_days.append(date_fr)
    
    return RunningDaysResponse(
        optimal_days=running_days,
        count=len(running_days)
    )


@router.get("/matches", response_model=MatchesResponse)
async def get_next_matches(count: int = 2):
    """
    Retourne les prochains matchs de l'équipe configurée.
    
    Args:
        count: Nombre de matchs à retourner (par défaut: 2)
    """
    from monday_report.core.config import settings
    
    matches = await FootballService.get_next_team_matches(count)
    return MatchesResponse(
        team_name=settings.team_name,
        matches=matches
    )


@router.get("/random-city", response_model=RandomCityResponse)
async def get_random_city():
    """
    Retourne une ville française aléatoire avec sa population et sa localisation.
    """
    city_info = await GeoService.get_random_french_city()
    return RandomCityResponse(city_info=city_info)
