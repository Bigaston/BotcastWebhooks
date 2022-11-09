# BotcastWebhooks
Botcast Webhooks est une version très simplifiée de feu Botcast, faite pour l'autohébergement.  
Le principe est basé sur un simple script python lancé par une crontab, que vous pouvez configurer pour lancer à l'interval de temps que vous voulez.

## Installation
Il vous faut Python3 d'installé, et les deux libs si dessous

Libs:
- feedparser
- requests

Ensuite:
- Commencez par clonner le répo `git clone https://github.com/Bigaston/BotcastWebhooks`
- Créez la base de donnée et le fichier de configuration `python3 index.py init`
- Créez un webhook dans le channel de votre choix sur Discord (Modifier le Salon > Intégration > Webhooks > Nouveau Webhook > Copier l'URL du Webhook)
- Collez le lien du webhook dans le fichier config.ini. Vous pouvez aussi modifier le message de base du bot, en ajoutant @everyone, @here. `__podcast__` sera remplacé par le nom du podcast en question
- Ajoutez le script à crontab via la commande `python3 index.py cron`

## Utilisation
Liste des commandes:
- init: Mise en place de la BDD et du fichier de config
- cron: Vous donne la ligne à ajouter au crontab
- add [flux]: Ajoute un flux à la BDD
- list: Liste tous les podcast
- remove [flux]: Retire le flux de la BDD
- force [flux]: Force l'envoit de la notification pour le flux
- fetch: Vérifie tous les flux et envoit une notification si besoin
- reset_guid [flux]: Renvoit de la notification de flux à la prochaine execution de fetch