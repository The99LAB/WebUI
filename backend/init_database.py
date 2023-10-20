import sqlite3
from notifications import NotificationManager, NotificationType

db = sqlite3.connect('database.db')
c = db.cursor()

# qemu_path = input("Enter qemu path: ") # /usr/bin/qemu-system-x86_64
qemu_path = "/usr/bin/qemu-system-x86_64"
novnc_ip = input("Enter novnc ip: ")
novnc_port = input("Enter novnc port: ")
novnc_protocool = input("Enter novnc protocool: ")
novnc_path = input("Enter novnc path: ") # vnc.html
# libvirt_domain_logs_path = input("Enter libvirt domain logs path: ") # /var/log/libvirt/qemu
libvirt_domain_logs_path = "/var/log/libvirt/qemu"

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
c.execute(f'''INSERT INTO "settings" ("id", "name", "value") VALUES (6, "libvirt domain logs path", "{libvirt_domain_logs_path}")''')
c.execute('''INSERT INTO "settings" ("id", "name", "value") VALUES (7, "login token expire", "3600")''')

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

# Create table docker_templates_locations
c.execute('''CREATE TABLE "docker_templates_locations" (
	"id"	INTEGER,
	"name"	TEXT NOT NULL,
	"url"	TEXT NOT NULL,
    "branch" TEXT NOT NULL,
	PRIMARY KEY("id")
);''')

# Create records in table docker_templates_locations
c.execute('''INSERT INTO "docker_templates_locations" ("id", "name", "url", "branch") VALUES ('1', 'VmManager Official', 'https://github.com/macOS-KVM/vm-manager-docker-templates.git', 'main')''')

# Create table docker_templates
c.execute('''CREATE TABLE "docker_templates" (
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
)''')

# finish work with database
db.commit()
db.close()

# Create welcome notification
NotificationManager().create_notification(NotificationType.INFO, "Welcome to Virtual Machine Manager", "Welcome to Virtual Machine Manager by Core-i99")
