from notifications import NotificationManager, NotificationType
from settings import SettingsManager, Setting, OvmfPath

qemu_path = "/usr/bin/qemu-system-x86_64"
novnc_ip = input("Enter novnc ip: ")
novnc_port = "6080"
novnc_protocool = "http"
novnc_path = "vnc.html"
libvirt_domain_logs_path = "/var/log/libvirt/qemu"

settings_manager = SettingsManager()

# Create settings
qemu_path_setting = Setting("qemu_path", qemu_path, "Path to qemu binary", verifyPath=True)
novnc_ip_setting = Setting("novnc_ip", novnc_ip, "IP address of novnc server", regex="^([0-9]{1,3}\.){3}[0-9]{1,3}$", regex_description="Only IP address allowed")
novnc_port_setting = Setting("novnc_port", novnc_port, "Port of novnc server", regex="^[0-9]+$", regex_description="Only numbers allowed")
novnc_protocool_setting = Setting("novnc_protocool", novnc_protocool, "Protocool of novnc server", regex="^(http|https)$", regex_description="Only http or https allowed")
novnc_path_setting = Setting("novnc_path", novnc_path, "Path to novnc server")
libvirt_domain_logs_path_setting = Setting("libvirt_domain_logs", libvirt_domain_logs_path, "Path to libvirt domain logs", verifyPath=True)
login_token_expire_setting = Setting("login_token_expire", "3600", "Login token expire time in seconds", regex="^[0-9]+$", regex_description="Only numbers allowed")
docker_template_repository_update = Setting("docker_template_repository_update", "0 0 * * *", "Cron expression for docker template repository update", regex="^(\*|[0-9]+(\/[0-9]+)?)(\s(\*|[0-9]+(\/[0-9]+)?)){4}$", regex_description="Only cron expression allowed")
settings_manager.create_setting(qemu_path_setting)
settings_manager.create_setting(novnc_ip_setting)
settings_manager.create_setting(novnc_port_setting)
settings_manager.create_setting(novnc_protocool_setting)
settings_manager.create_setting(novnc_path_setting)
settings_manager.create_setting(libvirt_domain_logs_path_setting)
settings_manager.create_setting(login_token_expire_setting)
settings_manager.create_setting(docker_template_repository_update)

# Create ovmf paths
ovmf_path = "/usr/share/OVMF/OVMF_CODE.fd"
ovmf_secureboot_path = "/usr/share/OVMF/OVMF_CODE.secboot.fd"
ovmf_path_setting = OvmfPath("OVMF", ovmf_path)
ovmf_secureboot_path_setting = OvmfPath("OVMF_Secureboot", ovmf_secureboot_path)
settings_manager.create_ovmf_path(ovmf_path_setting)
settings_manager.create_ovmf_path(ovmf_secureboot_path_setting)

# Create welcome notification
NotificationManager().create_notification(NotificationType.INFO, "Welcome to Virtual Machine Manager", "Welcome to Virtual Machine Manager by Core-i99")
