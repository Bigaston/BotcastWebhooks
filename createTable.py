import sqlite3

con = sqlite3.connect("base.db")
cur = con.cursor()

cur.execute("CREATE TABLE podcast(rss, guid)")