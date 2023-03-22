import sqlite3

db = sqlite3.connect('database.db')
c = db.cursor()

qemu_path = input("Enter qemu path: ")
novnc_ip = input("Enter novnc ip: ")
novnc_port = input("Enter novnc port: ")
novnc_protocool = input("Enter novnc protocool: ")
novnc_path = input("Enter novnc path: ")

# Create table settings
c.execute('''CREATE TABLE "settings" (
	"id"	INTEGER,
	"name"	TEXT,
	"value"	TEXT,
	PRIMARY KEY("id")
    )''')

# Create records in table settings
c.execute(f'''INSERT INTO "settings" ("id", "name", "value") VALUES (1, "qemu path", "{qemu_path}")''')
c.execute(f'''INSERT INTO "settings" ("id", "name", "value") VALUES (2, "novnc ip", "{novnc_ip}")''')
c.execute(f'''INSERT INTO "settings" ("id", "name", "value") VALUES (3, "novnc port", "{novnc_port}")''')
c.execute(f'''INSERT INTO "settings" ("id", "name", "value") VALUES (4, "novnc protocool", "{novnc_protocool}")''')
c.execute(f'''INSERT INTO "settings" ("id", "name", "value") VALUES (5, "novnc path", "{novnc_path}")''')

# Create table settings_ovmfpaths
c.execute('''CREATE TABLE "settings_ovmfpaths" (
	"id"	INTEGER,
	"name"	TEXT,
	"path"	TEXT,
	PRIMARY KEY("id")
    )''')

# Create records in table settings_ovmfpaths
c.execute('''INSERT INTO "settings_ovmfpaths" ("id", "name", "path") VALUES (1, "OVMF", "/usr/share/OVMF/OVMF_CODE.fd")''')
c.execute('''INSERT INTO "settings_ovmfpaths" ("id", "name", "path") VALUES (2, "OVMF Secureboot", "/usr/share/OVMF/OVMF_CODE.secboot.fd")''')

# finish work with database
db.commit()