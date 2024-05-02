# Server99 WebUI
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
- Create a file named `server99-WebUI.service` in `/etc/systemd/system/`
- Copy the following content into the file
```
[Unit]
Description=server99 WebUI
After=multi-user.target
[Service]
Type=simple
Restart=always
ExecStart=uvicorn main:app --host 0.0.0.0 --port 80
WorkingDirectory=/path/to/server99-WebUI
[Install]
WantedBy=multi-user.target
```
- Replace `/path/to/server99-WebUI` with the path to the WebUI directory
- Run `systemctl daemon-reload`
- Run `systemctl enable --now server99-WebUI.service`
- Run `systemctl status server99-WebUI.service` to check if the service is running