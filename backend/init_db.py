from db import get_session, create_db_and_tables
from notifications import NotificationManager, NotificationType, Notification
from settings import SettingsManager, Setting, OvmfPath, RegexRule
from settings.settingsException import SettingsException
import subprocess

settings_manager = SettingsManager()

try:
    hostname_setting = settings_manager.get_setting("hostname")
    print(f"Hostname setting exists with value: {hostname_setting.value}")
    # Write hostname to /etc/hostname
    with open("/etc/hostname", "w") as f:
        f.write(hostname_setting.value + "\n")
    subprocess.run(["hostnamectl", "set-hostname", hostname_setting.value], check=True)
except (SettingsException, subprocess.CalledProcessError):
    pass

create_db_and_tables()

qemu_path = "/usr/bin/qemu-system-x86_64"
novnc_ip = "127.0.0.1"
novnc_port = "6080"
novnc_protocol = "http"
novnc_path = "vnc.html"
libvirt_domain_logs_path = "/var/log/libvirt/qemu"


# Create settings
settings_to_create = [
    Setting("hostname", "server99.home", "Hostname of the server", hidden=True),
    Setting("qemu_path", qemu_path, "Path to qemu binary", verifyFile=True),
    Setting("novnc_ip", novnc_ip, "IP address of novnc server", [RegexRule("^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$", "Only IP address allowed")]),
    Setting("novnc_port", novnc_port, "Port of novnc server", [RegexRule("^[0-9]+$", "Only numbers allowed")]),
    Setting("novnc_protocol", novnc_protocol, "Protocol of novnc server", [RegexRule("^(http|https)$", "Only http or https allowed")]),
    Setting("novnc_path", novnc_path, "Path to novnc server"),
    Setting("libvirt_domain_logs", libvirt_domain_logs_path, "Path to libvirt domain logs", verifyDir=True),
    Setting("login_token_expire", "3600", "Login token expire time in seconds", [RegexRule("^[0-9]+$", "Only numbers allowed")]),
    Setting("docker_template_repository_update", "0 0 * * *", "Cron expression for docker template repository update", [RegexRule("^[0-9*\/]+$", "Only cron expression allowed")])
]

for setting in settings_to_create:
    try:
        settings_manager.get_setting(setting.name)
        print(f"Setting '{setting.name}' already exists, skipping creation")
    except SettingsException:
        settings_manager.create_setting(setting)
        print(f"Created setting '{setting.name}'")

# Create ovmf paths
ovmf_paths_to_create = [
    OvmfPath("OVMF", "/usr/share/OVMF/OVMF_CODE_4M.fd", "Path to OVMF firmware file"),
    OvmfPath("OVMF_SECBOOT", "/usr/share/OVMF/OVMF_CODE_4M.secboot.fd", "Path to OVMF secure boot firmware file")
]

for ovmf_path in ovmf_paths_to_create:
    try:
        settings_manager.get_ovmf_path(ovmf_path.name)
        print(f"OVMF path '{ovmf_path.name}' already exists, skipping creation")
    except SettingsException:
        settings_manager.create_ovmf_path(ovmf_path)
        print(f"Created OVMF path '{ovmf_path.name}'")