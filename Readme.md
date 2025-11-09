# 📧 Monday Briefing API

API FastAPI déployée sur AWS Lambda pour la génération et l'envoi automatique d'un briefing hebdomadaire personnalisé.

![Python](https://img.shields.io/badge/Python-3.11+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.118+-green)
![AWS Lambda](https://img.shields.io/badge/AWS-Lambda-orange)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## 📋 Description

Cette API génère automatiquement un briefing hebdomadaire contenant :
- 🌤️ **Météo** : Prévisions sur 7 jours selon la localisation renseignée
- 🏃 **Jours optimaux pour courir** : Sélection automatique basée sur la météo
- ⚽ **Matchs de football** : Les 2 prochains matchs de votre équipe favorite
- 🏙️ **Ville aléatoire** : Découverte d'une commune française avec sa population

Le briefing est **envoyé automatiquement par email tous les lundis à 8h** via AWS EventBridge.

---

## 🚀 Fonctionnalités

### **API REST **
- ✅ Endpoints individuels pour chaque composant du briefing
- ✅ Documentation interactive Swagger UI (`/docs`)
- ✅ Documentation ReDoc (`/redoc`)
- ✅ Configuration dynamique via endpoints PUT

### **Déploiement serverless**
- ✅ AWS Lambda + API Gateway
- ✅ Secrets sécurisés avec AWS Secrets Manager
- ✅ Scheduler automatique avec EventBridge
- ✅ Logs centralisés dans CloudWatch

### **Sécurité**
- 🔒 Clés API et credentials SMTP stockés dans Secrets Manager
- 🔒 Permissions IAM minimales
- 🔒 Variables sensibles jamais exposées dans le code

---

## 📡 API Endpoints

### **Briefing**
- `GET /monday-report` - Génère et envoie le briefing complet
- `GET /health` - Health check

### **Données individuelles**
- `GET /data/weather` - Prévisions météo 7 jours
- `GET /data/running-days` - Jours optimaux pour courir
- `GET /data/matches?count=2` - Prochains matchs de l'équipe
- `GET /data/random-city` - Ville française aléatoire

### **Configuration**
- `GET /config-check` - Vérifier la configuration SMTP
- `PUT /config/location` - Modifier la localisation GPS
- `PUT /config/team` - Changer l'équipe de football
- `PUT /config/email` - Mettre à jour l'email destinataire
- `PUT /cities/filter` - Configurer les filtres de villes

---

## 🏗️ Architecture

```
┌─────────────────┐
│  EventBridge    │──► Trigger tous les lundis à 8h
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Lambda         │──► Exécute le code Python
│  (FastAPI)      │
└────────┬────────┘
         │
         ├──► Secrets Manager (SMTP, API keys)
         ├──► API Météo (open-meteo.com)
         ├──► API Football (football-data.org)
         ├──► API Communes (geo.api.gouv.fr)
         │
         ▼
┌─────────────────┐
│  SMTP Server    │──► Envoi email
└─────────────────┘

┌─────────────────┐
│  API Gateway    │──► Accès HTTP public
└─────────────────┘
```

---

## 🛠️ Technologies

- **Backend** : FastAPI, Pydantic
- **Runtime** : Python 3.11
- **Serverless** : AWS Lambda, API Gateway, EventBridge
- **IaC** : AWS SAM (Serverless Application Model)
- **Sécurité** : AWS Secrets Manager
- **APIs externes** :
  - [Open-Meteo](https://open-meteo.com/) - Météo
  - [Football-Data.org](https://www.football-data.org/) - Matchs de foot
  - [API Géo](https://geo.api.gouv.fr/) - Communes françaises
- **Dépendances** : Pandas, Requests, httpx, boto3, Mangum

---

## 📦 Installation & Déploiement

### **Prérequis**
- Python 3.11+
- Poetry (gestion des dépendances)
- Docker Desktop (pour le build)
- AWS CLI configuré
- AWS SAM CLI

### **1. Clone le projet**
```bash
git clone https://github.com/leocoooo/Monday-Briefing-Improved-Version-.git
cd Monday-Briefing-Improved-Version-
```

### **2. Installation des dépendances**
```bash
poetry install
```

### **3. Configuration locale (.env)**
```bash
cp .env.example .env
# Édite .env avec tes vraies valeurs
```

### **4. Configuration AWS Secrets Manager**
Crée un secret nommé `monday-briefing/prod/config` avec :
```json
{
  "SMTP_HOST": "smtp.gmail.com",
  "SMTP_PORT": "587",
  "SMTP_USER": "ton_email@gmail.com",
  "SMTP_PASSWORD": "ton_mot_de_passe_app",
  "EMAIL_FROM": "ton_email@gmail.com",
  "EMAIL_TO": "destinataire@example.com",
  "FOOTBALL_DATA_API_KEY": "ta_clé_api_football"
}
```

### **5. Build & Déploiement**
```bash
# Build avec Docker
sam build --use-container

# Déploiement
sam deploy --guided
```

### **6. Configuration du scheduler**
L'envoi automatique est configuré pour **tous les lundis à 8h (heure de Paris)**.

Pour modifier l'horaire, éditer `template.yaml` :
```yaml
Schedule: 'cron(0 7 ? * MON *)'  # Lundi 8h Paris = 7h UTC
```

---

## 🧪 Tests

### **Test local**
```bash
# Lancer l'API localement
python main.py

# Tester un endpoint
curl http://localhost:8000/health
```

### **Test sur AWS**
```bash
# Via l'URL déployée
curl https://https://jd5x90vdo9.execute-api.eu-west-3.amazonaws.com/Prod//Prod/health

# Tester l'envoi du briefing (console Lambda)
# Event JSON :
{
  "source": "eventbridge",
  "action": "send_briefing"
}
```

---

## 📊 Monitoring

### **CloudWatch Logs**
```bash
# Voir les logs récents
aws logs tail /aws/lambda/MondayBriefingAPI --follow --region eu-west-3
```

### **Console AWS**
- Lambda : https://console.aws.amazon.com/lambda/
- API Gateway : https://console.aws.amazon.com/apigateway/
- EventBridge : https://console.aws.amazon.com/events/
- Secrets Manager : https://console.aws.amazon.com/secretsmanager/

---

## 🔧 Configuration avancée

### **Modifier l'horaire du briefing**
Voir [`SCHEDULER_CONFIG.md`](SCHEDULER_CONFIG.md) pour les détails.

### **Changer la région de déploiement**
```bash
# Dans samconfig.toml ou lors du deploy
aws configure  # Modifier la région par défaut
sam deploy --region eu-west-1
```

### **Filtrer les villes aléatoires**
```bash
curl -X PUT https://YOUR_URL/cities/filter \
  -H "Content-Type: application/json" \
  -d '{
    "min_population": 100000,
    "included_regions": ["Île-de-France", "Provence-Alpes-Côte d Azur"]
  }'
```

---

## 💰 Coûts AWS

Avec l'**offre gratuite AWS** (12 mois) :
- ✅ 1M requêtes Lambda/mois gratuites
- ✅ 1M requêtes API Gateway/mois gratuites
- ✅ EventBridge gratuit (règles limitées)

**Estimation pour usage typique** (1 envoi/semaine + quelques tests) :
- **Gratuit** pendant 12 mois
- Après : **< 1€/mois**

---

## 📝 Variables d'environnement

### **Variables publiques** (dans `template.yaml`)
```yaml
LATITUDE: "48.8566"         # Paris
LONGITUDE: "2.3522"
TIMEZONE: "Europe/Paris"
TEAM_ID: "524"              # PSG
TEAM_NAME: "Paris Saint-Germain"
```

### **Secrets** (dans AWS Secrets Manager)
- `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`
- `EMAIL_FROM`, `EMAIL_TO`
- `FOOTBALL_DATA_API_KEY`

---

## 🤝 Contribution

Les contributions sont les bienvenues ! Pour contribuer :

1. Fork le projet
2. Crée une branche (`git checkout -b feature/AmazingFeature`)
3. Commit tes changements (`git commit -m 'Add AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvre une Pull Request

---

## 📄 License

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

---

## 👤 Auteur

**Colin**
- Email: leocolin7002@gmail.com
- GitHub: [@leocoooo](https://github.com/leocoooo)

---

## 🙏 Remerciements

- [FastAPI](https://fastapi.tiangolo.com/) - Framework web moderne
- [Open-Meteo](https://open-meteo.com/) - API météo gratuite
- [Football-Data.org](https://www.football-data.org/) - API football
- [API Géo](https://geo.api.gouv.fr/) - Données communes françaises
- [AWS SAM](https://aws.amazon.com/serverless/sam/) - Déploiement serverless

---

## 📚 Documentation

- [Documentation API (Swagger)](https://YOUR_URL/Prod/docs)
- [Documentation API (ReDoc)](https://YOUR_URL/Prod/redoc)
- [Configuration Scheduler](SCHEDULER_CONFIG.md)

---

## 🐛 Problèmes connus

### **Fuseau horaire EventBridge**
EventBridge utilise UTC. Pour 8h Paris :
- **Hiver (UTC+1)** : `cron(0 7 ? * MON *)`
- **Été (UTC+2)** : `cron(0 6 ? * MON *)` (à ajuster manuellement)

### **Limitation APScheduler**
Le scheduler Python interne (APScheduler) ne fonctionne pas sur Lambda. Utiliser EventBridge pour la planification.

---

## 📈 Roadmap

- [ ] Support multi-langues
- [ ] Interface web pour la configuration
- [ ] Notifications Slack/Discord en plus de l'email
- [ ] Ajout d'autres sources de données (actualités, bourse, etc.)
- [ ] CI/CD avec GitHub Actions
- [ ] Tests unitaires et d'intégration

---

**⭐ Si ce projet vous a été utile, n'hésitez pas à laisser une étoile !**
