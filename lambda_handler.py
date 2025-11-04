"""
AWS Lambda handler pour Monday Briefing API
Utilise Mangum pour adapter FastAPI à AWS Lambda
Gère aussi les appels EventBridge pour l'envoi automatique
"""
from mangum import Mangum
from main import app
import asyncio
import json


async def send_briefing():
    """Envoie le briefing par email"""
    from monday_report.services.briefing_service import BriefingService
    from monday_report.services.email_service import EmailService
    
    report = await BriefingService.build_report()
    await EmailService.send_email("Briefing Hebdomadaire", report)
    return {"status": "success", "message": "Briefing envoyé"}


def lambda_handler(event, context):
    """
    Handler Lambda principal.
    Détecte si c'est un appel EventBridge ou API Gateway.
    """
    # Vérifier si c'est un événement EventBridge (scheduled)
    if event.get("source") == "eventbridge" or event.get("detail-type") == "Scheduled Event":
        print("Déclenchement EventBridge détecté - Envoi du briefing")
        result = asyncio.run(send_briefing())
        return {
            "statusCode": 200,
            "body": json.dumps(result)
        }
    
    # Sinon, c'est une requête API Gateway normale
    # Utiliser Mangum pour gérer FastAPI
    handler = Mangum(app, lifespan="off", api_gateway_base_path="/Prod")
    return handler(event, context)
