# WateringSystem


# Scheduling
    -   https://pypi.org/project/Flask-APScheduler/ 
    -   https://apscheduler.readthedocs.io/en/3.x/modules/triggers/cron.html
    -   https://betterprogramming.pub/introduction-to-apscheduler-86337f3bb4a6
    -   při prvním načtením projektu se přečte db, odkud získám všechny plánováné akce
    -   postupně si vytvořním jednotlivé záznamy pro danou akci

## Definice Db pro rutiny
```
    -   RUTINY
    -   id
    -   nazev rutiny
    -   popisek (co má dělat)
    -   id_zarizení
    -   every_day
    -   every_month
    -   time_start
    -   time_stop
    -   is_active
    
    ------
    
    -   RUTINY_DNY
    -   id
    -   routine_id
    -   day_id
    
    ------
    
    -   DNY
    -   id
    -   den
    
```
 