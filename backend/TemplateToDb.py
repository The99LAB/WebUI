import sqlite3
from git import Repo
import os
import tempfile
import json

db = sqlite3.connect('database.db')
c = db.cursor()

# The urls of the template repository
c.execute('''SELECT * FROM docker_templates_locations''')
template_locations = c.fetchall()

# Clear all the templates from the database
c.execute('''DELETE FROM docker_templates''')
db.commit()

for repo in template_locations:
    print(f"Repo id: {repo[0]}\nRepo name: {repo[1]}\nRepo url: {repo[2]}\nRepo branch: {repo[3]}\n\n")

    repository_id = repo[0]
    repository_name = repo[1]
    repository_url = repo[2]
    repository_branch = repo[3]

    # We store the repo in a tmp folder provided by the 'tempfile' module
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

            c.execute(f'''INSERT INTO "docker_templates" ("template_repository_id", "name", "maintainer", "description", "webui", "image", "url", "config") VALUES ("{repository_id}", "{json_name}", "{json_maintainer}", "{json_description}", ?, ?, ?, ?)''', (json_webui ,png_data, json_url, json_config))

            db.commit()
        else:
            print("Both files do not exist")
            print("Missing files, skipping this template")

db.close()
