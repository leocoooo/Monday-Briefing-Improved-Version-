"""
Module pour récupérer les secrets depuis AWS Secrets Manager
"""
import json
import os
import boto3
from botocore.exceptions import ClientError
import logging

logger = logging.getLogger(__name__)

# Cache pour éviter de requêter Secrets Manager à chaque appel
_secrets_cache = None


def get_secrets(secret_name: str = "monday-briefing/prod/config", region_name: str = "eu-west-3") -> dict:
    """
    Récupère les secrets depuis AWS Secrets Manager.
    Utilise un cache pour éviter les appels répétés.
    
    Args:
        secret_name: Nom du secret dans Secrets Manager
        region_name: Région AWS
        
    Returns:
        dict: Dictionnaire contenant les secrets
    """
    global _secrets_cache
    
    # Si déjà en cache, retourner le cache
    if _secrets_cache is not None:
        return _secrets_cache
    
    # Si on est en environnement local (pas Lambda), retourner dict vide
    if not os.getenv("AWS_EXECUTION_ENV"):
        logger.info("Environnement local détecté, utilisation des variables d'environnement")
        return {}
    
    try:
        # Créer le client Secrets Manager
        session = boto3.session.Session()
        client = session.client(
            service_name='secretsmanager',
            region_name=region_name
        )
        
        # Récupérer le secret
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
        
        # Parser le JSON
        secret_string = get_secret_value_response['SecretString']
        secrets_dict = json.loads(secret_string)
        
        # Mettre en cache
        _secrets_cache = secrets_dict
        logger.info(f"Secrets récupérés depuis {secret_name}")
        
        return secrets_dict
        
    except ClientError as e:
        logger.error(f"Erreur lors de la récupération des secrets: {e}")
        return {}
    except Exception as e:
        logger.error(f"Erreur inattendue: {e}")
        return {}


def get_secret_value(key: str, default=None):
    """
    Récupère une valeur spécifique depuis les secrets.
    
    Args:
        key: Clé du secret à récupérer
        default: Valeur par défaut si la clé n'existe pas
        
    Returns:
        La valeur du secret ou la valeur par défaut
    """
    secrets = get_secrets()
    return secrets.get(key, default)
