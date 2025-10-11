import httpx
import random
from monday_report.models.city import FrenchCommune
from monday_report.core.config import city_filter
from monday_report.utils.departements import DEPARTEMENTS_REGIONS

class GeoService:
    BASE_URL = "https://geo.api.gouv.fr/communes"

    @staticmethod
    async def get_random_french_city() -> str:
        params = {"fields": "nom,population,code,codeDepartement", "format": "json"}

        async with httpx.AsyncClient() as client:
            resp = await client.get(GeoService.BASE_URL, params=params, timeout=15)
            resp.raise_for_status()
            communes = resp.json()

        if not communes:
            return "Aucune commune trouvée."

        filtered = [
            c for c in communes
            if c.get("population", 0) >= city_filter.min_population
        ]

        if city_filter.max_population:
            filtered = [c for c in filtered if c["population"] <= city_filter.max_population]
        if city_filter.included_regions:
            filtered = [
                c for c in filtered
                if DEPARTEMENTS_REGIONS.get(c["codeDepartement"]) in city_filter.included_regions
            ]
        if city_filter.excluded_regions:
            filtered = [
                c for c in filtered
                if DEPARTEMENTS_REGIONS.get(c["codeDepartement"]) not in city_filter.excluded_regions
            ]

        if not filtered:
            return "Aucune ville ne correspond aux critères."

        commune = FrenchCommune(**random.choice(filtered))
        return commune.to_string()
