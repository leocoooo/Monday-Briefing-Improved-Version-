import httpx
from datetime import datetime
import pytz
from monday_report.core.config import settings
from monday_report.models.football import PSGMatchInfo

class FootballService:
    BASE_URL = "https://api.football-data.org/v4"

    @staticmethod
    async def get_next_psg_matches(count: int = 2):
        if not settings.football_data_api_key:
            return ["⚠️ API key non configurée."]

        url = f"{FootballService.BASE_URL}/teams/{settings.team_id}/matches"
        headers = {"X-Auth-Token": settings.football_data_api_key}
        params = {"status": "SCHEDULED"}

        async with httpx.AsyncClient() as client:
            resp = await client.get(url, headers=headers, params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json()

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
