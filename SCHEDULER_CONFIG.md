# ⏰ Configuration du Scheduler EventBridge

## 📅 Planification actuelle

**Tous les lundis à 8h00 (heure de Paris)**
- Cron expression: `cron(0 7 ? * MON *)`
- Timezone: UTC (7h UTC = 8h Paris en hiver, 6h UTC = 8h Paris en été)

## 🔧 Modifier l'horaire

### Dans `template.yaml`, modifie la ligne :

```yaml
Schedule: 'cron(0 7 ? * MON *)'
```

### Format cron AWS EventBridge :
```
cron(Minutes Heures Jour-du-mois Mois Jour-de-la-semaine Année)
```

### Exemples :

**Tous les lundis à 9h (Paris) :**
```yaml
Schedule: 'cron(0 8 ? * MON *)'
```

**Tous les jours à 8h :**
```yaml
Schedule: 'cron(0 7 ? * * *)'
```

**Tous les lundis et vendredis à 8h :**
```yaml
Schedule: 'cron(0 7 ? * MON,FRI *)'
```

**Premier lundi du mois à 8h :**
```yaml
Schedule: 'cron(0 7 ? * MON#1 *)'
```

## ⚠️ Note importante sur le fuseau horaire

EventBridge utilise **UTC**. Pour Paris (UTC+1 en hiver, UTC+2 en été) :
- **8h Paris hiver** = `7` en UTC
- **8h Paris été** = `6` en UTC

👉 Actuellement configuré pour 8h heure de Paris en **hiver**.

## 🧪 Tester manuellement

Pour tester l'envoi sans attendre le lundi, tu peux :

1. **Via l'API** (appel manuel) :
```bash
curl https://jd5x90vdo9.execute-api.eu-west-3.amazonaws.com/Prod/monday-report
```

2. **Via la console Lambda** :
   - Va sur AWS Lambda console
   - Sélectionne `MondayBriefingAPI`
   - Onglet "Test"
   - Crée un événement test avec :
   ```json
   {
     "source": "eventbridge",
     "action": "send_briefing"
   }
   ```
   - Clique "Test"

## 🔕 Désactiver le scheduler

Dans `template.yaml`, change :
```yaml
Enabled: true
```
en
```yaml
Enabled: false
```

Puis redéploie avec `sam deploy`.

## 📊 Vérifier les logs

Les logs d'envoi sont dans **CloudWatch Logs** :
1. AWS Console → CloudWatch → Log groups
2. Cherche `/aws/lambda/MondayBriefingAPI`
3. Vérifie les logs après chaque déclenchement

---

**Après modification, redéploie avec :**
```bash
sam build --use-container
sam deploy
```
