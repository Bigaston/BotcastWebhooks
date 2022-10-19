import sqlite3
import feedparser
import requests
import configparser
import sys
import os

bdd = os.path.join(os.path.dirname(os.path.realpath(__file__)), "base.db")

def get_entry_date(entry):
  return entry.get("published_parsed")

# Sans Arguments
if len(sys.argv) == 1:
  print("BotcastPython par Bigaston (HELP)")
  print("Liste des commandes:")
  print("- init: Mise en place de la BDD et du fichier de config")
  print("- cron: Vous donne la ligne à ajouter au crontab")
  print("- add [flux]: Ajoute un flux à la BDD")
  print("- list: Liste tous les podcast")
  print("- remove [flux]: Retire le flux de la BDD")
  print("- force [flux]: Force l'envoit de la notification pour le flux")
  print("- fetch: Vérifie tous les flux et envoit une notification si besoin")
  print("- reset_guid [flux]: Renvoit de la notification de flux à la prochaine execution de fetch")
else:
  if sys.argv[1] == "init" or sys.argv[1] == "setup":
    print("Initialisation du système")

    if not os.path.exists(bdd):
      con = sqlite3.connect(bdd)
      cur = con.cursor()

      cur.execute("CREATE TABLE podcast(rss, guid)")

      print("> Base crée")

    else:
      print("> Base déjà existante, skip")
    
    if not os.path.exists("config.ini"):
      config = configparser.ConfigParser()
      config['DEFAULT'] = {
        "DefaultMessage": ":tada: Un nouvel épisode de **__podcast__** est disponible!",
        "Webhook": ""
      }

      with open('config.ini', 'w') as configfile:
        config.write(configfile)

      print("> Fichier de config initialisé")
    else:
      print("> Fichier de config déjà existant, skip")
    
    print("Travail terminé. Pensez à modifier config.ini pour coller le bon webhook")
    exit()
  # Affichage du cron
  elif sys.argv[1] == "cron":
    print("Ajouter la ligne si dessous à la crontab de votre user avec 'crontab -e'")
    print("*/5 * * * * /bin/python3 " + os.getcwd() + "/index.py fetch")
  # Ajout de podcast
  elif sys.argv[1] == "add":
    if len(sys.argv) == 2:
      print("Il manque le flux RSS!")
      exit()

    feed = feedparser.parse(sys.argv[2])

    entries = feed.entries
    entries.sort(reverse=True, key=get_entry_date)

    if len(entries) == 0:
      print("Erreur: Pas d'épisode dans le flux!")
      exit()

    con = sqlite3.connect(bdd)
    cur = con.cursor()

    cur.execute("INSERT INTO podcast VALUES(?, ?)", (sys.argv[2], entries[0].guid))
    con.commit()

    print("Podcast " + sys.argv[2] + " ajouté")
  
  # Affichage des podcasts
  elif sys.argv[1] == "list":
    con = sqlite3.connect(bdd)
    cur = con.cursor()

    res = cur.execute("SELECT * FROM podcast")

    print("Liste des podcasts")
    for podcast in res.fetchall():
      print("> " + podcast[0])

  # Suppression des podcasts
  elif sys.argv[1] == "remove" or sys.argv[1] == "delete":
    if len(sys.argv) == 2:
      print("Il manque le flux RSS!")
      exit()

    print("Podcast " + sys.argv[2] + " supprimé")

    con = sqlite3.connect(bdd)
    cur = con.cursor()

    cur.execute("DELETE FROM podcast WHERE rss = ?", (sys.argv[2],))
    con.commit()

  elif sys.argv[1] == "force":
    if len(sys.argv) == 2:
      print("Il manque le flux RSS!")
      exit()

    print("Envoit de la notification pour " + sys.argv[2])

    config = configparser.ConfigParser()
    config.read("config.ini", encoding='utf-8')

    feed = feedparser.parse(sys.argv[2])

    entries = feed.entries
    entries.sort(reverse=True, key=get_entry_date)
    
    con = sqlite3.connect(bdd)
    cur = con.cursor()

    cur.execute("UPDATE podcast SET guid = ? WHERE rss = ?", (entries[0].guid, sys.argv[2]))
    con.commit()

    r = requests.post(config["DEFAULT"]["Webhook"], json={
      "content": config["DEFAULT"]["DefaultMessage"].replace("__podcast__", feed.feed.title), 
      "embeds": [{
        "title": entries[0].title,
        "description": entries[0].content[0].value[0:4095],
        "url": entries[0].links[0].href,
        "thumbnail": {
          "url": entries[0].image.href
        },
        "fields": [{
          "name": ":headphones:",
          "value": "[Ecouter l'épisode](" + entries[0].links[0].href + ")",
          "inline": True
        }, {
          "name": ":link:",
          "value": "[Visiter le site du podcast](" + feed.feed.link + ")",
          "inline": True
        }],
        "color": 0xff9100
      }]
    })
  # Récupération des données
  elif sys.argv[1] == "fetch":
    config = configparser.ConfigParser()
    config.read("config.ini", encoding='utf-8')

    con = sqlite3.connect(bdd)
    cur = con.cursor()

    res = cur.execute("SELECT * FROM podcast")

    print("Fetch des flux")

    for podcast in res.fetchall():
      feed = feedparser.parse(podcast[0])

      entries = feed.entries
      entries.sort(reverse=True, key=get_entry_date)

      if entries[0].guid != podcast[1]:
        print("> Envoit du dernier épisode de " + feed.feed.title)
        # Changement du GUID

        cur.execute("UPDATE podcast SET guid = ? WHERE rss = ?", (entries[0].guid, podcast[0]))
        con.commit()

        r = requests.post(config["DEFAULT"]["Webhook"], json={
          "content": config["DEFAULT"]["DefaultMessage"].replace("__podcast__", feed.feed.title), 
          "embeds": [{
            "title": entries[0].title,
            "description": entries[0].content[0].value[0:4095],
            "url": entries[0].links[0].href,
            "thumbnail": {
              "url": entries[0].image.href
            },
            "fields": [{
              "name": ":headphones:",
              "value": "[Ecouter l'épisode](" + entries[0].links[0].href + ")",
              "inline": True
            }, {
              "name": ":link:",
              "value": "[Visiter le site du podcast](" + feed.feed.link + ")",
              "inline": True
            }],
            "color": 0xff9100
          }]
        })
  elif sys.argv[1] == "reset_guid":
    if len(sys.argv) == 2:
      print("Il manque le flux RSS!")
      exit()

    con = sqlite3.connect(bdd)
    cur = con.cursor()

    cur.execute("UPDATE podcast SET guid = ? WHERE rss = ?", ("", sys.argv[2]))
    con.commit()

    print("Podcast " + sys.argv[2] + " reinitialisé")
