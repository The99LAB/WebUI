import os
import subprocess
import shutil

output = subprocess.run('quasar build', shell=True, cwd='frontend')

# copy files from dist/spa to backend using python

# if static and templates folder exists, delete them
if os.path.exists('backend/static'):
    shutil.rmtree('backend/static')
if os.path.exists('backend/templates'):
    shutil.rmtree('backend/templates')

# create static and templates folder in backend
os.mkdir('backend/static')
os.mkdir('backend/templates')
shutil.move('frontend/dist/spa/index.html', 'backend/templates')

# move files inside dist.spa to backend/static
for file in os.listdir('frontend/dist/spa'):
    shutil.move('frontend/dist/spa/' + file, 'backend/static')

# zip backend folder
shutil.make_archive('WebUI-build', 'zip', 'backend')