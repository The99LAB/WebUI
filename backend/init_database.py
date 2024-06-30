from notifications import NotificationManager, NotificationType, Notification
from settings import SettingsManager, Setting, OvmfPath, RegexRule

qemu_path = "/usr/bin/qemu-system-x86_64"
novnc_ip = input("Enter novnc ip: ")
novnc_port = "6080"
novnc_protocol = "http"
novnc_path = "vnc.html"
libvirt_domain_logs_path = "/var/log/libvirt/qemu"

settings_manager = SettingsManager()

# Create settings
qemu_path_setting = Setting("qemu_path", qemu_path, "Path to qemu binary", verifyFile=True)
novnc_ip_setting = Setting("novnc_ip", novnc_ip, "IP address of novnc server", [RegexRule("^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$", "Only IP address allowed")])
novnc_port_setting = Setting("novnc_port", novnc_port, "Port of novnc server", [RegexRule("^[0-9]+$", "Only numbers allowed")])
novnc_protocol_setting = Setting("novnc_protocol", novnc_protocol, "Protocol of novnc server", [RegexRule("^(http|https)$", "Only http or https allowed")])
novnc_path_setting = Setting("novnc_path", novnc_path, "Path to novnc server")
libvirt_domain_logs_path_setting = Setting("libvirt_domain_logs", libvirt_domain_logs_path, "Path to libvirt domain logs", verifyDir=True)
login_token_expire_setting = Setting("login_token_expire", "3600", "Login token expire time in seconds", [RegexRule("^[0-9]+$", "Only numbers allowed")])
docker_template_repository_update = Setting("docker_template_repository_update", "0 0 * * *", "Cron expression for docker template repository update", [RegexRule("^[0-9*\/]+$", "Only cron expression allowed")])
settings_manager.create_setting(qemu_path_setting)
settings_manager.create_setting(novnc_ip_setting)
settings_manager.create_setting(novnc_port_setting)
settings_manager.create_setting(novnc_protocol_setting)
settings_manager.create_setting(novnc_path_setting)
settings_manager.create_setting(libvirt_domain_logs_path_setting)
settings_manager.create_setting(login_token_expire_setting)
settings_manager.create_setting(docker_template_repository_update)

# Create ovmf paths
ovmf_path = "/usr/share/ovmf/OVMF.fd"
ovmf_path_setting = OvmfPath("OVMF", ovmf_path)
settings_manager.create_ovmf_path(ovmf_path_setting)

# Create welcome notification
NotificationManager().create_notification(Notification(NotificationType.INFO, "Welcome to the Server99 WebUI", ""))
