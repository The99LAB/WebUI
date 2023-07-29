# VmManager
WebUI for managing libvirt based virtual machines and docker containers

## Usage (production)
- Download the latest release
- Extract the archive
- Run `python3 init_database.py`
- Run `uvicorn main:app --host 0.0.0.0 --port 80`

## Usage (development)
- Download the source code
- Run `python3 init_database.py`
- Run `uvicorn main:app --reload --host 0.0.0.0 --port 8000`

## Run as a service
- Create a file named `VmManager.service` in `/etc/systemd/system/`
- Copy the following content into the file
```
[Unit]
Description=VmManager
After=multi-user.target
[Service]
Type=simple
Restart=always
ExecStart=uvicorn main:app --host 0.0.0.0 --port 80
WorkingDirectory=/path/to/VmManager
[Install]
WantedBy=multi-user.target
```
- Replace `/path/to/VmManager` with the path to the VmManager directory
- Run `systemctl daemon-reload`
- Run `systemctl enable --now VmManager.service`
- Run `systemctl status VmManager.service` to check if the service is running