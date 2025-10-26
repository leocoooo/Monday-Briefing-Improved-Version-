import httpx
import logging
from datetime import datetime
import pytz
from monday_report.core.config import settings
from monday_report.models.football import PSGMatchInfo

logger = logging.getLogger(__name__)

class FootballService:
    BASE_URL = "https://api.football-data.org/v4"

    @staticmethod
    async def get_next_team_matches(count: int = 2):
        if not settings.football_data_api_key:
            msg = f"⚠️ API key non configurée pour {settings.team_name}."
            # log to console so scheduled jobs surface the problem
            logger.warning(msg)
            print(msg)
            return [msg]

        url = f"{FootballService.BASE_URL}/teams/{settings.team_id}/matches"
        headers = {"X-Auth-Token": settings.football_data_api_key}
        params = {"status": "SCHEDULED"}

        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(url, headers=headers, params=params, timeout=10)
                resp.raise_for_status()
                data = resp.json()
        except httpx.HTTPStatusError as e:
            status = e.response.status_code
            if status == 403:
                msg = (f"⚠️ Erreur d'accès aux données de {settings.team_name} (ID: {settings.team_id}). "
                       "Vérifiez votre clé API et vos droits d'accès sur football-data.org")
                logger.warning(msg)
                print(msg)
                return [msg]
            elif status == 404:
                msg = (f"⚠️ Équipe {settings.team_name} (ID: {settings.team_id}) non trouvée. "
                       "Vérifiez l'ID de l'équipe sur football-data.org")
                logger.warning(msg)
                print(msg)
                return [msg]
            else:
                msg = f"Erreur {status} pour {settings.team_name}: {str(e)}"
                logger.warning(msg)
                print(msg)
                return [msg]
        except Exception as e:
            msg = f"⚠️ Erreur inattendue pour {settings.team_name}: {str(e)}"
            logger.error(msg)
            print(msg)
            return [msg]

        matches = data.get("matches", [])
        result = []
        for match in matches[:count]:
            utc_dt = datetime.fromisoformat(match["utcDate"].replace("Z", "+00:00"))
            tz = pytz.timezone(settings.timezone)
            local_dt = utc_dt.astimezone(tz)

            is_home = match["homeTeam"]["id"] == settings.team_id
            opponent = match["awayTeam"]["name"] if is_home else match["homeTeam"]["name"]
            competition = match.get("competition", {}).get("name", "")
            venue = "Domicile" if is_home else "Extérieur"

            date_fr = local_dt.strftime('%A %d %B %Y à %H:%M').capitalize()
            result.append(PSGMatchInfo(
                date=date_fr,
                venue=venue,
                opponent=opponent,
                competition=competition
            ).to_string())

        return result
