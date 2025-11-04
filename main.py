from fastapi import FastAPI
import uvicorn
import os

from monday_report.core.lifespan import lifespan
from monday_report.utils.locale_utils import set_french_locale

# Import des routers
from monday_report.api import (
    endpoints_briefing,
    endpoints_config,
    endpoints_health,
    endpoints_data,
)


# Initialisation de la locale française 
loc = set_french_locale()
if loc:
    print(f"Locale appliquée : {loc}")
else:
    print("Impossible d'appliquer la locale française — affichage des dates en ISO.")

# Déterminer si on est sur Lambda (ajouter le root_path)
root_path = "/Prod" if os.getenv("AWS_EXECUTION_ENV") else ""

# Initialisation de l'app FastAPI 
app = FastAPI(
    title="Monday Briefing API",
    description="""API pour la génération automatique et l'envoi par mail d'un briefing hebdomadaire procurant : 
    la météo autour d'une localisation, les jours optimaux de la semaine pour aller courir, 
    les deux prochains matchs de foot de l'équipe choisie, une ville française aléatoire et sa population.""",
    version="2.1.0",
    lifespan=lifespan,
    root_path=root_path
)


# Routes
app.include_router(endpoints_briefing.router)
app.include_router(endpoints_config.router)
app.include_router(endpoints_health.router)
app.include_router(endpoints_data.router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
