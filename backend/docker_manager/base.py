import os
import sqlite3
import docker

def database():
    database_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database.db')
    conn = sqlite3.connect(database_path)

    # Set row_factory to return a dictionary
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Create table docker_templates_locations if not exists and insert default location
    cursor.execute('''SELECT count(name) FROM sqlite_master WHERE type='table' AND name='docker_templates_locations' ''')
    if cursor.fetchone()[0] == 0:
        cursor.execute('''
        CREATE TABLE "docker_templates_locations" (
            "id"	INTEGER,
            "name"	TEXT NOT NULL,
            "url"	TEXT NOT NULL,
            "branch" TEXT NOT NULL,
            "last_update"	TEXT,
            PRIMARY KEY("id")
        );''')

        cursor.execute('''INSERT INTO "docker_templates_locations" ("id", "name", "url", "branch") VALUES ('1', 'Server99 Official', 'https://github.com/99-industries/WebUI-docker-templates.git', 'main')''')

    # Create table docker_templates if not exists
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS "docker_templates" (
        "id"	INTEGER,
        "template_repository_id"	INTEGER NOT NULL,
        "name"	TEXT NOT NULL,
        "maintainer"	TEXT NOT NULL,
        "description"	TEXT,
        "webui"	TEXT NOT NULL,
        "image"	BLOB,
        "url"	TEXT NOT NULL,
        "config"	TEXT NOT NULL,
        PRIMARY KEY("id"),
        FOREIGN KEY("template_repository_id") REFERENCES "docker_templates_locations"("id")
    );''')

    # Create table docker_containers if not exists
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS "docker_containers" (
        "id"	TEXT,
        "container_type"	TEXT NOT NULL,
        "webui"	TEXT NOT NULL,
        "config"	TEXT NOT NULL,
        PRIMARY KEY("id")
    );''')
    conn.commit()
    return conn

def docker_client():
    return docker.from_env()