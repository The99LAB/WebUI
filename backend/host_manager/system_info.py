from .libvirt_con import libvirt_connection
from .hostManagerException import HostManagerException
from xml.etree import ElementTree as ET
import distro
import os
import psutil
import humanize
from datetime import datetime
import subprocess

class SystemInfo:
    def __init__(self):
        self.libvirt_conn = libvirt_connection.connection
        self._cpu_model = "Unknown"
        self._motherboard = "Unknown"
        self._memory_size = 0
        self._os = "Unknown"
        self._linux_kernel = "Unknown"
        self._uptime = "Unknown"
        self.libvirt_sysinfo_xml = ET.fromstring(self.libvirt_conn.getSysinfo())
        self.get_cpu_info()
        self.get_motherboard_info()
        self.get_memory_size()
        self.get_os_info()
        self.get_linux_kernel_info()
        self.get_uptime()
        pass
    
    @property
    def hostname(self):
        return self.libvirt_conn.getHostname()
    
    @property
    def cpu_model(self):
        return self._cpu_model
    
    @property
    def motherboard(self):
        return self._motherboard
    
    @property
    def memory_size(self):
        return f"{self._memory_size} GB"
    
    @property
    def os(self):
        return self._os
    
    @property
    def linux_kernel_version(self):
        return self._linux_kernel
    
    @property
    def uptime(self):
        return self._uptime
    
    def setHostname(self, hostname):
        try:
            subprocess.run(["hostnamectl", "set-hostname", hostname], check=True)
        except subprocess.CalledProcessError:
            raise HostManagerException("Failed to set hostname")

    def get_cpu_info(self):
        with open('/proc/cpuinfo') as f:
            for line in f:
                if line.startswith('model name'):
                    self._cpu_model = line.split(':')[1].strip()
                    break

    def get_motherboard_info(self):
        if self.libvirt_sysinfo_xml.find('baseBoard') is not None:
            manufacturer = self.libvirt_sysinfo_xml.find('baseBoard/entry[@name="manufacturer"]').text
            product = self.libvirt_sysinfo_xml.find('baseBoard/entry[@name="product"]').text
            version = self.libvirt_sysinfo_xml.find('baseBoard/entry[@name="version"]').text
            self._motherboard = f"{manufacturer} {product} {version}"
    
    def get_os_info(self):
        self._os = distro.name(pretty=True)

    def get_linux_kernel_info(self):
        self._linux_kernel = os.uname()[2]

    def get_memory_size(self):
        for memory_device in self.libvirt_sysinfo_xml.findall('memory_device'):
            self._memory_size += int(memory_device.find("entry[@name='size']").text.replace(" GB", ""))
    
    def get_uptime(self):
        self._uptime = humanize.precisedelta(datetime.now() - datetime.fromtimestamp(psutil.boot_time()), minimum_unit="minutes", format="%0.0f")