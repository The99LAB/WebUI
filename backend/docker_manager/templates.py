from .base import database
from git import Repo
import tempfile
import os
import json
from datetime import datetime
import base64

class Templates:
    def __init__(self):
        self.db_conn = database()
        self.db_cursor = self.db_conn.cursor()
    
    def getLocations(self):
        return self.db_cursor.execute('SELECT * FROM docker_templates_locations').fetchall()

    def getLocation(self, id):
        return self.db_cursor.execute('SELECT * FROM docker_templates_locations WHERE id = ?', (id,)).fetchone()
    
    def addLocation(self, name, url, branch):
        self.db_cursor.execute('INSERT INTO docker_templates_locations (name, url, branch) VALUES (?, ?, ?)', (name, url, branch))
        self.db_conn.commit()
    
    def editLocation(self, id, name, url, branch):
        self.db_cursor.execute('UPDATE docker_templates_locations SET name = ?, url = ?, branch = ? WHERE id = ?', (name, url, branch, id))
        self.db_conn.commit()

    def updateLocation(self, id):
        print("update template location", id)
        # Remove all templates associated with this location
        self.db_cursor.execute('DELETE FROM docker_templates WHERE template_repository_id = ?', (id,))

        # Download the new templates using git
        template_location_data = self.getLocation(id)
        repository_url = template_location_data['url']
        repository_branch = template_location_data['branch']
        temp_dir = tempfile.TemporaryDirectory()

        # Clone the repo
        Repo.clone_from(repository_url, temp_dir.name, branch=repository_branch)

        # List the files in the repo
        print(f"Files in repo: {os.listdir(temp_dir.name)}")

        templates_dir = os.path.join(temp_dir.name, 'Templates')

        for folder in os.listdir(templates_dir):
            json_file = os.path.join(templates_dir, folder, f"{folder}.json")
            print(f"Json file: {json_file}")

            png_file = os.path.join(templates_dir, folder, f"{folder}.png")
            print(f"Png file: {png_file}")

            if os.path.isfile(json_file) and os.path.isfile(png_file):
                print("Both files exist")

                # Read the json file
                with open(json_file, 'r') as f:
                    json_data = json.load(f)
                
                # Read the png file
                with open(png_file, 'rb') as f:
                    png_data = f.read()

                json_name = json_data['name']
                json_maintainer = json_data['maintainer']
                json_description = json_data['description']
                json_webui = json.dumps(json_data['webui'])
                json_url = json.dumps(json_data['url'])
                json_config = json.dumps(json_data['config'])

                self.db_cursor.execute(f'''INSERT INTO "docker_templates" ("template_repository_id", "name", "maintainer", "description", "webui", "image", "url", "config") VALUES ("{id}", "{json_name}", "{json_maintainer}", "{json_description}", ?, ?, ?, ?)''', (json_webui ,png_data, json_url, json_config))
            else:
                print("One or more files are missing")
                print(f"Json file exists: {os.path.isfile(json_file)}")
                print(f"Png file exists: {os.path.isfile(png_file)}")
                print(f"Skipping this template: {folder}")

        # Update the last_update field
        self.db_cursor.execute('UPDATE docker_templates_locations SET last_update = ? WHERE id = ?', (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), id))
        self.db_conn.commit()

    def deleteLocation(self, id):
        self.db_cursor.execute('DELETE FROM docker_templates_locations WHERE id = ?', (id,))
        self.db_conn.commit()

    def convertTemplate(self, template):
        if type(template) is not dict:
            template = dict(template)
        template['image'] = base64.b64encode(template['image']).decode('utf-8')
        template['webui'] = json.loads(template['webui'])
        template['url'] = json.loads(template['url'])
        template['config'] = json.loads(template['config'])
        return template

    def getTemplates(self):
        templates =  self.db_cursor.execute('SELECT * FROM docker_templates').fetchall()
        dictrows = [dict(row) for row in templates]
        for item in dictrows:
            item = self.convertTemplate(item)
        return dictrows
            
    def getTemplate(self, id):
        return self.convertTemplate(self.db_cursor.execute('SELECT * FROM docker_templates WHERE id = ?', (id,)).fetchone())

    def deleteTemplate(self, id):
        self.db_cursor.execute('DELETE FROM docker_templates WHERE id = ?', (id,))
        self.db_conn.commit()