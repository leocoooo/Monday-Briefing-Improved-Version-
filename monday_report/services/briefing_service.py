from datetime import datetime
import pytz
from monday_report.core.config import settings
from monday_report.services.football_service import FootballService
from monday_report.services.weather_service import WeatherService
from monday_report.services.geo_service import GeoService

class BriefingService:
    @staticmethod
    async def build_report() -> str:
        tz = pytz.timezone(settings.timezone)
        now = datetime.now(tz)
        generated_at = now.strftime('%A %d %B %Y à %H:%M').capitalize()

        psg_matches = await FootballService.get_next_psg_matches(2)
        weather_days = await WeatherService.get_week_weather()
        random_city = await GeoService.get_random_french_city()

        report = [
            "═" * 60,
            "📅 BRIEFING HEBDOMADAIRE",
            f"Généré le {generated_at}",
            "═" * 60,
            "",
            "⚽ PROCHAINS MATCHS DU PSG",
            "─" * 60,
            *psg_matches,
            "",
            "🌤️ MÉTÉO (7 JOURS)",
            "─" * 60,
        ]

        running_days = []
        for day in weather_days:
            report.append(day.to_string())
            if day.is_good_for_running():
                date_fr = datetime.strptime(day.date, '%Y-%m-%d').strftime('%A %d %B').capitalize()
                running_days.append(date_fr)

        report += [
            "",
            "🏃 JOURS OPTIMAUX POUR COURIR",
            "─" * 60,
            "  " + (", ".join(running_days) if running_days else "Aucun jour optimal"),
            "",
            "🏙️ VILLE ALÉATOIRE",
            "─" * 60,
            f"  {random_city}",
            "",
            "═" * 60,
        ]

        return "\n".join(report)
