from typing import Optional, List
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from monday_report.core.config import settings, city_filter
from monday_report.core.scheduler import scheduler
# scheduled job function (défini dans lifespan)
from monday_report.core.lifespan import scheduled_monday_job

router = APIRouter(prefix="", tags=["config"])


@router.get("/config-check")
async def config_check():
    """
    Vérifie rapidement si la configuration SMTP est complète.
    """
    smtp_configured = all([
        settings.smtp_host,
        settings.smtp_user,
        settings.smtp_password,
        settings.email_from,
        settings.email_to
    ])

    return {
        "smtp_configured": smtp_configured,
        "config_status": {
            "smtp_host": "✅ configuré" if settings.smtp_host else "❌ manquant",
            "smtp_port": settings.smtp_port,
            "smtp_user": "✅ configuré" if settings.smtp_user else "❌ manquant",
            "smtp_password": "✅ configuré" if settings.smtp_password else "❌ manquant",
            "email_from": "✅ configuré" if settings.email_from else "❌ manquant",
            "email_to": "✅ configuré" if settings.email_to else "❌ manquant",
        },
        "note": "Si tous ne sont pas configurés, l'email ne sera pas envoyé et un fichier sera créé à la place."
    }


# ---- PUT models ----
class LocationUpdate(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)


@router.put("/config/location")
async def update_location(location: LocationUpdate):
    """Met à jour les coordonnées GPS utilisées pour la météo."""
    settings.latitude = location.latitude
    settings.longitude = location.longitude
    return {
        "status": "updated",
        "new_config": {
            "latitude": settings.latitude,
            "longitude": settings.longitude
        }
    }


class TeamUpdate(BaseModel):
    team_id: int
    team_name: str


@router.put("/config/team")
async def update_team(team: TeamUpdate):
    """Change l'équipe suivie pour les matchs."""
    settings.team_id = team.team_id
    settings.team_name = team.team_name
    return {
        "status": "updated",
        "new_config": {
            "team_id": settings.team_id,
            "team_name": settings.team_name
        }
    }


class EmailUpdate(BaseModel):
    email_to: str


@router.put("/config/email")
async def update_email(email_data: EmailUpdate):
    """Met à jour l'adresse email destinataire pour les briefings."""
    settings.email_to = email_data.email_to
    return {
        "status": "updated",
        "new_config": {
            "email_to": settings.email_to
        }
    }


class SchedulerDayUpdate(BaseModel):
    day_of_week: str
    hour: int = Field(8, ge=0, le=23)
    minute: int = Field(0, ge=0, le=59)


@router.put("/scheduler/day")
async def update_scheduler_day(schedule_data: SchedulerDayUpdate):
    """
    Modifie le jour/heure du job programmé.
    Remplace le job 'monday_briefing' par un nouveau job avec l'ID identique.
    """
    valid_days = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
    day = schedule_data.day_of_week.lower()
    if day not in valid_days:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid day. Must be one of: {', '.join(valid_days)}"
        )

    # retire l'ancien job si présent (no-op sinon)
    try:
        scheduler.remove_job('monday_briefing')
    except Exception:
        pass

    # ajoute le job avec la nouvelle planification
    scheduler.add_job(
        scheduled_monday_job,
        'cron',
        day_of_week=day,
        hour=schedule_data.hour,
        minute=schedule_data.minute,
        id='monday_briefing'
    )

    return {
        "status": "updated",
        "new_schedule": {
            "day_of_week": schedule_data.day_of_week,
            "time": f"{schedule_data.hour:02d}:{schedule_data.minute:02d}"
        }
    }


class CityFilterUpdate(BaseModel):
    min_population: Optional[int] = Field(None, ge=0)
    max_population: Optional[int] = Field(None, ge=0)
    included_regions: Optional[List[str]] = None
    excluded_regions: Optional[List[str]] = None
    included_departments: Optional[List[str]] = None
    excluded_departments: Optional[List[str]] = None


@router.put("/cities/filter")
async def update_city_filter(filter_data: CityFilterUpdate):
    """
    Met à jour les critères de filtrage pour la sélection aléatoire de communes.
    """
    if (filter_data.min_population is not None and
        filter_data.max_population is not None and
        filter_data.max_population < filter_data.min_population):
        raise HTTPException(
            status_code=400,
            detail="max_population must be greater than min_population"
        )

    if filter_data.min_population is not None:
        city_filter.min_population = filter_data.min_population
    if filter_data.max_population is not None:
        city_filter.max_population = filter_data.max_population
    if filter_data.included_regions is not None:
        city_filter.included_regions = filter_data.included_regions
    if filter_data.excluded_regions is not None:
        city_filter.excluded_regions = filter_data.excluded_regions
    if filter_data.included_departments is not None:
        city_filter.included_departments = filter_data.included_departments
    if filter_data.excluded_departments is not None:
        city_filter.excluded_departments = filter_data.excluded_departments

    return {
        "status": "updated",
        "current_filters": {
            "min_population": city_filter.min_population,
            "max_population": city_filter.max_population,
            "included_regions": city_filter.included_regions,
            "excluded_regions": city_filter.excluded_regions,
            "included_departments": city_filter.included_departments,
            "excluded_departments": city_filter.excluded_departments
        }
    }
