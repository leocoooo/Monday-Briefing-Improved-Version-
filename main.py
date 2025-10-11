from fastapi import FastAPI
import uvicorn

from monday_report.core.lifespan import lifespan
from monday_report.utils.locale_utils import set_french_locale

# Import des routers
from monday_report.api import (
    endpoints_briefing,
    endpoints_config,
    endpoints_health,
    endpoints_test 
)


# --- Initialisation de la locale française ---
loc = set_french_locale()
if loc:
    print(f"✅ Locale appliquée : {loc}")
else:
    print("⚠️ Impossible d'appliquer la locale française — affichage des dates en ISO.")


# --- Création de l'application FastAPI ---
app = FastAPI(
    title="Monday Briefing API",
    description="API pour la génération automatique du briefing hebdomadaire (météo, PSG, ville aléatoire).",
    version="2.1.0",
    lifespan=lifespan
)


# --- Montage des routes ---
app.include_router(endpoints_briefing.router)
app.include_router(endpoints_config.router)
app.include_router(endpoints_health.router)
app.include_router(endpoints_test.router)


# --- Point d'entrée principal (pour exécution directe) ---
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
