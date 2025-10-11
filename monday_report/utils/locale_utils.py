# utilitaires pour la gestion de la locale (FR)
import locale
from typing import Optional


def set_french_locale() -> Optional[str]:
    """
    Tente d'initialiser la locale française et retourne la locale appliquée
    ou None si aucune locale n'a pu être définie.
    """
    tried = [
        'fr_FR.UTF-8',
        'fr_FR',
        'French_France.1252',
        'fr'
    ]
    for loc in tried:
        try:
            locale.setlocale(locale.LC_TIME, loc)
            return loc
        except Exception:
            continue
    return None


def format_date_fr(dt, fmt: str = '%A %d %B %Y à %H:%M') -> str:
    """
    Formatte un datetime en chaîne lisible en français (si la locale FR est disponible).
    Utiliser set_french_locale() au démarrage de l'app pour tenter d'appliquer la locale.
    """
    try:
        return dt.strftime(fmt)
    except Exception:
        # fallback safe
        return dt.isoformat()
