import sqlite3

db = sqlite3.connect('database.db')
c = db.cursor()

# Delete table docker_containers
c.execute('''DROP TABLE IF EXISTS "docker_containers"''')

# Create table docker_containers
c.execute('''CREATE TABLE "docker_containers" (
	"id"	TEXT,
	"container_type"	TEXT NOT NULL,
	"webui"	TEXT NOT NULL,
	"config"	TEXT NOT NULL,
	PRIMARY KEY("id")
);''')

db.commit()
db.close()