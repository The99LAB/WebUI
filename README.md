# VmManager
Web UI for managing libvirt based virtual machines

## Usage (production)
- Download the latest release
- Extract the archive
- Run `gunicorn --worker-class eventlet -w 1 main:app --bind :80`

## Usage (development)
- Download the source code
- Run `python3 main.py`
