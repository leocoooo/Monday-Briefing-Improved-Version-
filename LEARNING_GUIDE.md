# 📚 Ce que j'ai appris : Déploiement d'une API FastAPI sur AWS Lambda

**Guide pédagogique - Session du 5 novembre 2025**

---

## 🎯 Objectif de la session

Déployer une API FastAPI existante sur AWS Lambda avec :
- ✅ Infrastructure serverless (Lambda + API Gateway)
- ✅ Sécurisation des secrets (Secrets Manager)
- ✅ Envoi automatique planifié (EventBridge)

---

## 1️⃣ Concepts clés appris

### **Lambda vs serveur traditionnel**

| **Serveur traditionnel** | **AWS Lambda** |
|--------------------------|----------------|
| Tourne 24/7 | Se réveille à la demande |
| Coût fixe mensuel | Paye uniquement les exécutions |
| Tu gères les mises à jour | AWS gère tout |
| Besoin d'un processus continu | Éphémère (se détruit après chaque requête) |

**Conséquence importante :**
- ❌ APScheduler (scheduler Python) ne fonctionne PAS sur Lambda
- ✅ Il faut utiliser EventBridge (scheduler AWS externe)

---

### **Serverless = Gestion d'événements**

```
Événement ──► Lambda ──► Traitement ──► Réponse
    ▲                                      │
    │                                      ▼
API Gateway                            Résultat
EventBridge                           (JSON, email, etc.)
S3 Upload
etc.
```

**Lambda ne "tourne" pas en permanence**, elle est **déclenchée** par des événements.

---

## 2️⃣ Architecture mise en place

```
┌──────────────────────────────────────────────────────────────┐
│                      UTILISATEUR / CLIENT                     │
└────────────────────────┬─────────────────────────────────────┘
                         │ HTTP Request
                         ▼
┌────────────────────────────────────────────────────────────────┐
│                      API GATEWAY (REST)                        │
│  - Route /Prod/health, /Prod/data/weather, etc.              │
│  - Gère les requêtes HTTP                                     │
└────────────────────────┬───────────────────────────────────────┘
                         │ Invoke
                         ▼
┌────────────────────────────────────────────────────────────────┐
│                    AWS LAMBDA FUNCTION                         │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │ lambda_handler.py (Point d'entrée)                       │ │
│  │  ├─ Détecte si c'est API Gateway ou EventBridge         │ │
│  │  ├─ API Gateway ──► Mangum ──► FastAPI                  │ │
│  │  └─ EventBridge ──► Envoie briefing par email           │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │ FastAPI Application (main.py)                            │ │
│  │  ├─ Routers (endpoints_briefing, endpoints_data, etc.)  │ │
│  │  ├─ Services (weather, football, email, etc.)           │ │
│  │  └─ Models (Pydantic)                                    │ │
│  └──────────────────────────────────────────────────────────┘ │
└────────────┬───────────────────────────┬───────────────────────┘
             │                           │
             ▼                           ▼
┌─────────────────────┐      ┌──────────────────────────┐
│  SECRETS MANAGER    │      │  APIs EXTERNES           │
│  ├─ SMTP            │      │  ├─ Open-Meteo (météo)   │
│  ├─ Football API    │      │  ├─ Football-Data.org    │
│  └─ Email config    │      │  └─ API Geo (communes)   │
└─────────────────────┘      └──────────────────────────┘

┌────────────────────────────────────────────────────────────────┐
│                    EVENTBRIDGE (SCHEDULER)                     │
│  Règle cron : Tous les lundis à 8h                            │
│  ──► Déclenche Lambda ──► Envoie le briefing par email       │
└────────────────────────────────────────────────────────────────┘
```

---

## 3️⃣ Technologies et outils utilisés

### **Côté développement**
- **Poetry** : Gestionnaire de dépendances Python moderne
- **FastAPI** : Framework web rapide et moderne
- **Mangum** : Adaptateur FastAPI ↔ Lambda (traduit les événements AWS en requêtes HTTP)
- **Pydantic** : Validation des données

### **Côté AWS**
- **AWS Lambda** : Exécution serverless du code Python
- **API Gateway** : Expose l'API en HTTP/REST
- **EventBridge** : Scheduler externe (remplace APScheduler)
- **Secrets Manager** : Stockage sécurisé des clés API/SMTP
- **CloudWatch Logs** : Logs centralisés

### **Infrastructure as Code (IaC)**
- **AWS SAM** (Serverless Application Model) : Outil de déploiement
  - `template.yaml` : Définit toute l'infrastructure
  - Génère automatiquement CloudFormation

### **Outils CLI**
- **AWS CLI** : Interaction avec AWS en ligne de commande
- **SAM CLI** : Build et déploiement de l'infrastructure

---

## 4️⃣ Flux de déploiement complet

### **Étape par étape :**

```
1. Code Python local (FastAPI)
   │
   ├─ poetry add mangum          # Ajouter l'adaptateur Lambda
   ├─ poetry export > requirements.txt
   │
2. Créer lambda_handler.py       # Point d'entrée Lambda
   │
3. Créer template.yaml           # Infrastructure SAM
   │
4. Configurer AWS CLI
   │
   ├─ aws configure              # Access Key + Secret Key
   │
5. Build avec Docker
   │
   ├─ sam build --use-container  # Compile dans environnement Python 3.11
   │                             # (identique à Lambda)
   │
6. Déploiement
   │
   ├─ sam deploy --guided        # 1ère fois : configure tout
   │   ou                        # ├─ Crée bucket S3
   ├─ sam deploy                 # │  ├─ Upload le code
   │                             # │  ├─ Crée Lambda
   │                             # │  ├─ Crée API Gateway
   │                             # │  └─ Crée EventBridge rule
   │
7. Configuration post-déploiement
   │
   ├─ Créer secret dans Secrets Manager (SMTP, API keys)
   ├─ Redéployer pour appliquer les changements
   │
8. API en production ! 🚀
```

---

## 5️⃣ Commandes essentielles

### **Configuration initiale (une seule fois)**

```bash
# 1. Installer les outils
# Télécharger AWS CLI : https://awscli.amazonaws.com/AWSCLIV2.msi
# Télécharger SAM CLI : https://github.com/aws/aws-sam-cli/releases/latest/download/AWS_SAM_CLI_64_PY3.msi

# 2. Configurer AWS credentials
aws configure
# AWS Access Key ID: [ta clé IAM]
# AWS Secret Access Key: [ton secret]
# Default region: eu-west-3
# Default output format: json

# 3. Vérifier l'installation
aws --version
sam --version
```

### **Workflow de développement et déploiement**

```bash
# 1. Ajouter une dépendance Python
poetry add nom_package

# 2. Exporter requirements.txt (pour Lambda)
poetry export -f requirements.txt --output requirements.txt --without-hashes

# 3. Builder l'application (avec Docker)
sam build --use-container

# 4. Tester localement (optionnel)
sam local start-api  # Lance l'API en local sur http://127.0.0.1:3000

# 5. Déployer sur AWS
sam deploy  # Utilise samconfig.toml (créé lors du --guided)

# 6. Voir les logs en temps réel
aws logs tail /aws/lambda/MondayBriefingAPI --follow --region eu-west-3
```

### **Gestion des secrets**

```bash
# Créer un secret (via CLI)
aws secretsmanager create-secret \
  --name monday-briefing/prod/config \
  --secret-string file://secret.json \
  --region eu-west-3

# Lire un secret
aws secretsmanager get-secret-value \
  --secret-id monday-briefing/prod/config \
  --region eu-west-3
```

---

## 6️⃣ Fichiers clés du projet

### **Structure projet**

```
monday_report/
├── lambda_handler.py          # 🔑 Point d'entrée Lambda
├── main.py                    # FastAPI app principale
├── template.yaml              # 🔑 Infrastructure SAM
├── requirements.txt           # 🔑 Dépendances (pour Lambda)
├── pyproject.toml             # Dépendances (pour Poetry local)
├── samconfig.toml             # Configuration SAM (auto-généré)
├── .env                       # Variables locales (JAMAIS commit!)
├── .env.example               # Template de config
├── README.md                  # Documentation
├── SCHEDULER_CONFIG.md        # Guide du scheduler
│
├── monday_report/
│   ├── api/                   # Endpoints FastAPI
│   │   ├── endpoints_briefing.py
│   │   ├── endpoints_data.py
│   │   ├── endpoints_config.py
│   │   └── endpoints_health.py
│   │
│   ├── core/
│   │   ├── config.py          # 🔑 Settings + chargement secrets
│   │   ├── secrets.py         # 🔑 Interface Secrets Manager
│   │   ├── lifespan.py
│   │   └── scheduler.py       # (inutile sur Lambda)
│   │
│   ├── services/              # Logique métier
│   │   ├── briefing_service.py
│   │   ├── email_service.py
│   │   ├── weather_service.py
│   │   ├── football_service.py
│   │   └── geo_service.py
│   │
│   ├── models/                # Pydantic models
│   └── utils/                 # Helpers
│
└── .aws-sam/                  # 🔧 Généré par SAM (ne pas commit)
    └── build/                 # Code packagé prêt pour Lambda
```

---

## 7️⃣ Interactions entre systèmes

### **Requête HTTP normale (utilisateur → API)**

```
1. Utilisateur fait une requête HTTP
   │
   ├─ curl https://API_GATEWAY_URL/Prod/health
   │
2. API Gateway reçoit la requête
   │
   ├─ Transforme en événement AWS Lambda format
   │
3. Lambda est invoquée
   │
   ├─ lambda_handler(event, context) est appelé
   │   │
   │   ├─ Détecte que c'est API Gateway (pas "source": "eventbridge")
   │   │
   │   ├─ Passe à Mangum
   │   │   │
   │   │   ├─ Mangum convertit l'événement Lambda en requête ASGI
   │   │   │
   │   │   └─ FastAPI traite la requête
   │   │       │
   │   │       ├─ Router → Endpoint → Service
   │   │       │
   │   │       └─ Retourne réponse JSON
   │   │
   │   └─ Mangum convertit la réponse FastAPI en format Lambda
   │
4. API Gateway reçoit la réponse Lambda
   │
   ├─ Transforme en réponse HTTP
   │
5. Utilisateur reçoit la réponse
```

### **Déclenchement automatique (EventBridge → Lambda)**

```
1. EventBridge détecte l'heure programmée
   │
   ├─ Tous les lundis à 7h UTC (= 8h Paris)
   │
2. EventBridge invoque Lambda
   │
   ├─ Envoie un événement avec : {"source": "eventbridge", ...}
   │
3. Lambda est invoquée
   │
   ├─ lambda_handler(event, context) est appelé
   │   │
   │   ├─ Détecte "source": "eventbridge"
   │   │
   │   ├─ Appelle directement send_briefing()
   │   │   │
   │   │   ├─ BriefingService.build_report()
   │   │   │   ├─ WeatherService.get_week_weather()
   │   │   │   ├─ FootballService.get_next_team_matches()
   │   │   │   └─ GeoService.get_random_french_city()
   │   │   │
   │   │   └─ EmailService.send_email(report)
   │   │       └─ Se connecte au serveur SMTP
   │   │           └─ Envoie l'email
   │   │
   │   └─ Retourne {"status": "success"}
   │
4. Email envoyé ! 📧
```

### **Accès aux secrets (Lambda → Secrets Manager)**

```
1. Lambda démarre (cold start ou warm)
   │
2. config.py s'initialise
   │
   ├─ Détecte AWS_EXECUTION_ENV (= on est sur Lambda)
   │
   ├─ Appelle secrets.py → get_secrets()
   │   │
   │   ├─ Crée un client boto3 Secrets Manager
   │   │
   │   ├─ Appelle secretsmanager.get_secret_value()
   │   │   │
   │   │   └─ AWS vérifie les permissions IAM
   │   │       ├─ ✅ Lambda a le rôle avec secretsmanager:GetSecretValue
   │   │       └─ ✅ Ressource autorisée : monday-briefing/*
   │   │
   │   ├─ Reçoit le JSON chiffré
   │   │
   │   ├─ Déchiffre automatiquement (géré par AWS)
   │   │
   │   └─ Parse le JSON
   │
   ├─ Met en cache (évite de requêter à chaque fois)
   │
   └─ Configure settings avec les valeurs
       ├─ settings.smtp_password = secrets["SMTP_PASSWORD"]
       ├─ settings.football_api_key = secrets["FOOTBALL_DATA_API_KEY"]
       └─ etc.
```

---

## 8️⃣ Différences local vs Lambda

| **Aspect** | **En local** | **Sur Lambda** |
|------------|--------------|----------------|
| **Environnement** | Ton PC (Windows, Python 3.13) | Linux, Python 3.11 (géré par AWS) |
| **Variables d'env** | `.env` (python-dotenv) | Variables Lambda + Secrets Manager |
| **Scheduler** | APScheduler fonctionne | ❌ APScheduler inutile → EventBridge |
| **Démarrage** | `python main.py` (tourne en continu) | Lambda démarre/s'arrête à chaque requête |
| **Logs** | Console locale | CloudWatch Logs |
| **Dépendances** | Installées par Poetry dans `.venv` | Packagées dans le ZIP Lambda |
| **Build** | Pas de build nécessaire | `sam build` requis |

---

## 9️⃣ Problèmes rencontrés et solutions

### **Problème 1 : Version Python (3.13 vs 3.11)**

**Erreur :**
```
Binary validation failed for python, searched for python in following locations [...] 
which did not satisfy constraints for runtime: python3.11
```

**Cause :** SAM cherche Python 3.11 mais trouve Python 3.13 sur la machine.

**Solution :** Utiliser Docker pour builder dans un environnement Python 3.11
```bash
sam build --use-container
```

---

### **Problème 2 : Compilation numpy/pandas**

**Erreur :**
```
NumPy requires GCC >= 9.3
```

**Cause :** Versions récentes de numpy (2.x) nécessitent un compilateur trop récent pour l'environnement Lambda.

**Solution :** Forcer des versions plus anciennes
```bash
poetry add "numpy<2.0" "pandas<2.3"
poetry export -f requirements.txt --output requirements.txt --without-hashes
```

---

### **Problème 3 : Documentation FastAPI (403 sur /docs)**

**Erreur :**
```
Failed to load /openapi.json: 403
```

**Cause :** FastAPI génère des URLs sans le préfixe `/Prod/` requis par API Gateway.

**Solution :** Configurer `root_path` dans FastAPI
```python
root_path = "/Prod" if os.getenv("AWS_EXECUTION_ENV") else ""
app = FastAPI(root_path=root_path, ...)
```

Et dans `lambda_handler.py` :
```python
handler = Mangum(app, api_gateway_base_path="/Prod")
```

---

### **Problème 4 : AWS CLI ne fonctionne pas dans Git Bash**

**Cause :** Problème de PATH Windows avec Git Bash.

**Solution :** Utiliser **CMD** ou **PowerShell** pour les commandes AWS/SAM.

---

## 🔟 Concepts avancés compris

### **Cold Start vs Warm Start**

```
┌─────────────────────────────────────────────────────────┐
│ COLD START (première invocation ou après inactivité)   │
├─────────────────────────────────────────────────────────┤
│ 1. AWS télécharge le code Lambda                       │
│ 2. Initialise l'environnement Python                   │
│ 3. Importe les modules (FastAPI, boto3, etc.)         │
│ 4. Exécute le code d'initialisation                   │
│ 5. Appelle get_secrets() (Secrets Manager)            │
│ 6. Exécute le handler                                 │
│                                                         │
│ ⏱️ Durée : ~1-3 secondes                               │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ WARM START (invocations suivantes)                     │
├─────────────────────────────────────────────────────────┤
│ 1. Environnement déjà prêt                             │
│ 2. Modules déjà importés                              │
│ 3. Secrets en cache                                   │
│ 4. Exécute directement le handler                     │
│                                                         │
│ ⏱️ Durée : ~50-200 ms                                  │
└─────────────────────────────────────────────────────────┘
```

**Optimisation :** Le cache des secrets (`_secrets_cache`) évite de requêter Secrets Manager à chaque appel.

---

### **Infrastructure as Code (IaC)**

**Avant (manuel) :**
- Se connecter à la console AWS
- Créer Lambda à la main
- Créer API Gateway à la main
- Configurer les permissions IAM
- Créer EventBridge rule
- Tout refaire si on veut un environnement de test

**Avec SAM (template.yaml) :**
```yaml
Resources:
  MondayBriefingFunction:
    Type: AWS::Serverless::Function
    Properties:
      Handler: lambda_handler.lambda_handler
      Events:
        MondaySchedule:
          Type: Schedule
          Schedule: 'cron(0 7 ? * MON *)'
```

Un seul `sam deploy` :
- ✅ Crée tout automatiquement
- ✅ Reproductible (même infra en dev/prod)
- ✅ Versionnable (Git)
- ✅ Destruction facile : `sam delete`

---

### **Sécurité par couches (Defense in Depth)**

```
┌──────────────────────────────────────────────────┐
│ Niveau 1 : .gitignore                            │
│ └─ .env jamais commit sur GitHub                │
└──────────────────────────────────────────────────┘
                    ▼
┌──────────────────────────────────────────────────┐
│ Niveau 2 : IAM (moindre privilège)              │
│ └─ Lambda a UNIQUEMENT le droit de :            │
│    ├─ Écrire dans CloudWatch Logs               │
│    └─ Lire monday-briefing/* dans Secrets Mgr   │
└──────────────────────────────────────────────────┘
                    ▼
┌──────────────────────────────────────────────────┐
│ Niveau 3 : Secrets Manager                      │
│ └─ Secrets chiffrés au repos (AES-256)          │
│    ├─ Logs d'accès (audit)                      │
│    └─ Rotation possible                         │
└──────────────────────────────────────────────────┘
                    ▼
┌──────────────────────────────────────────────────┐
│ Niveau 4 : Chiffrement en transit               │
│ └─ HTTPS (API Gateway, SMTP TLS)                │
└──────────────────────────────────────────────────┘
```

**Résultat :** Même si quelqu'un a accès à la console Lambda, il ne voit pas les secrets en clair.

---

## 1️⃣1️⃣ Points clés à retenir

### **Lambda n'est pas un serveur traditionnel**
- ✅ Serverless = pas de gestion de serveur
- ✅ Éphémère = code exécuté puis détruit
- ✅ Event-driven = déclenché par des événements
- ❌ Pas de processus continu (APScheduler ne fonctionne pas)

### **Adaptateur nécessaire pour FastAPI**
- **Mangum** traduit événements Lambda ↔ requêtes ASGI/HTTP
- Permet d'utiliser FastAPI sans modification majeure

### **Secrets Manager > Variables d'environnement**
- Variables d'env : visibles dans la console (pas idéal pour secrets)
- Secrets Manager : chiffrés, auditables, rotation possible

### **EventBridge = Cron externe**
- Remplace APScheduler sur Lambda
- Scheduler géré par AWS (pas dans ton code)

### **Infrastructure as Code (SAM)**
- `template.yaml` = définition déclarative de l'infra
- Reproductible, versionnable, automatisable

### **Docker pour le build**
- Garantit compatibilité binaire (Windows → Linux Lambda)
- Compile les dépendances dans le bon environnement

---

## 1️⃣2️⃣ Commandes mémo (résumé ultra-court)

```bash
# Setup (une fois)
aws configure

# Workflow standard
poetry add package                # Ajouter dépendance
poetry export > requirements.txt  # Exporter pour Lambda
sam build --use-container         # Builder (Docker requis)
sam deploy                        # Déployer

# Monitoring
aws logs tail /aws/lambda/MondayBriefingAPI --follow

# Nettoyage
sam delete  # Supprime toute l'infrastructure
```

---

## 1️⃣3️⃣ Ressources pour aller plus loin

### **Documentation officielle**
- [FastAPI](https://fastapi.tiangolo.com/)
- [AWS Lambda](https://docs.aws.amazon.com/lambda/)
- [AWS SAM](https://docs.aws.amazon.com/serverless-application-model/)
- [Mangum](https://mangum.io/)

### **Concepts à approfondir**
- **Lambda Layers** : Partager des dépendances entre Lambdas
- **CloudFormation** : Le langage sous-jacent de SAM
- **Step Functions** : Orchestrer plusieurs Lambdas
- **DynamoDB** : Base NoSQL serverless
- **S3 Events** : Déclencher Lambda sur upload fichier
- **API Gateway Authorizers** : Ajouter de l'authentification

### **Optimisations possibles**
- Utiliser Lambda Layers pour numpy/pandas (réduire taille package)
- Ajouter un CloudFront devant API Gateway (cache, CDN)
- Utiliser X-Ray pour tracer les requêtes
- Mettre en place des alarmes CloudWatch
- CI/CD avec GitHub Actions

---

## 🎓 Conclusion

**Ce que tu sais faire maintenant :**
- ✅ Adapter une API FastAPI pour AWS Lambda
- ✅ Utiliser SAM pour déployer de l'infrastructure
- ✅ Gérer des secrets de manière sécurisée
- ✅ Mettre en place un scheduler serverless
- ✅ Comprendre l'architecture event-driven
- ✅ Débugger avec CloudWatch Logs
- ✅ Différencier local vs cloud

**Prochaines étapes suggérées :**
1. Ajouter des tests unitaires (pytest)
2. Mettre en place CI/CD (GitHub Actions)
3. Créer un environnement de staging (dev/prod)
4. Ajouter de l'authentification (API keys, JWT)
5. Monitorer avec CloudWatch Dashboards

---

**🚀 Félicitations ! Tu maîtrises maintenant le déploiement serverless sur AWS !**

---

*Document créé le 5 novembre 2025*  
*Projet : Monday Briefing API*  
*Auteur : Colin*
