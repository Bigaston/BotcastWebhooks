import sqlite3
import feedparser
import requests
import time
import configparser

config = configparser.ConfigParser()
config.read("config.ini", encoding='utf-8')

con = sqlite3.connect("base.db")
cur = con.cursor()

res = cur.execute("SELECT * FROM podcast")

def get_entry_date(entry):
  return entry.get("published_parsed")

for podcast in res.fetchall():
  feed = feedparser.parse(podcast[0])

  entries = feed.entries
  entries.sort(reverse=True, key=get_entry_date)



  if entries[0].guid != podcast[1]:
    # Changement du GUID
    cur.execute("UPDATE podcast SET guid = ? WHERE rss = ?", (entries[0].guid, podcast[0]))
    con.commit()

    print(entries[0])

    print(time.mktime(entries[0].published_parsed))

    print(entries[0].published_parsed)

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

    print(r.status_code)
    print(r.text)
