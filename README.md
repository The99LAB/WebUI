# VmManager
Web UI for managing libvirt based virtual machines

## Usage (production)
- Download the latest release
- Extract the archive
- Run `python3 init_database.py`
- Run `uwsgi --http :80 --gevent 1000 --master --wsgi-file main.py --callable app`

## Usage (development)
- Download the source code
- Run `python3 init_database.py`
- Run `python3 main.py`

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
ExecStart=uwsgi --http :80 --gevent 1000 --master --wsgi-file main.py --callable app
WorkingDirectory=/path/to/VmManager
[Install]
WantedBy=multi-user.target
```
- Replace `/path/to/VmManager` with the path to the VmManager directory
- Run `systemctl daemon-reload`
- Run `systemctl enable --now VmManager.service`
- Run `systemctl status VmManager.service` to check if the service is running