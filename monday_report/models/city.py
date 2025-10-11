from pydantic import BaseModel, Field, ConfigDict
from monday_report.utils.departements import DEPARTEMENTS_NOMS, DEPARTEMENTS_REGIONS

class FrenchCommune(BaseModel):
    nom: str
    population: int
    code: str
    code_departement: str = Field(alias="codeDepartement")

    model_config = ConfigDict(populate_by_name=True)

    def to_string(self) -> str:
        dept_nom = DEPARTEMENTS_NOMS.get(self.code_departement, f"département {self.code_departement}")
        region = DEPARTEMENTS_REGIONS.get(self.code_departement, "région inconnue")
        return f"{self.nom} — {dept_nom}, {region} — {self.population:,} habitants"
