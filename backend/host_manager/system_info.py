from .libvirt_con import libvirt_connection
from .hostManagerException import HostManagerException
from xml.etree import ElementTree as ET
import distro
import os
import psutil
import humanize
from datetime import datetime
import subprocess
import re

class PcieDevice:
    def __init__(self, device_xml):
        device_xml = ET.fromstring(device_xml)
        iommu_group_object = device_xml.find('./capability/iommuGroup')
        self.iommu_group = None
        if iommu_group_object is not None:
            self.iommu_group = int(iommu_group_object.get('number'))
        self.path = device_xml.find('name').text.replace('pci_', '').replace('_', ':')
        product_object = device_xml.find('./capability/product')
        self.product_name = product_object.text
        if self.product_name is None:
            self.product_name = ""
        self.product_id = product_object.get('id')
        vendor_object = device_xml.find('./capability/vendor')
        self.vendor_name = vendor_object.text
        self.vendor_id = vendor_object.get('id')
        self.driver = ""
        try:
            self.driver = device_xml.find('./driver/name').text
        except AttributeError:
            pass
        self.domain = str(hex(int(device_xml.find('./capability/domain').text))).replace('0x', '')
        self.bus = str(hex(int(device_xml.find('./capability/bus').text))).replace('0x', '')
        self.slot = str(hex(int(device_xml.find('./capability/slot').text))).replace('0x', '')
        self.function = str(hex(int(device_xml.find('./capability/function').text))).replace('0x', '')
        self.label = f"{self.path} {self.vendor_name} {self.product_name}"
    
    @property
    def json(self):
        return {
            'iommu_group': self.iommu_group,
            'path': self.path,
            'product_name': self.product_name,
            'product_id': self.product_id,
            'vendor_name': self.vendor_name,
            'vendor_id': self.vendor_id,
            'driver': self.driver,
            'domain': self.domain,
            'bus': self.bus,
            'slot': self.slot,
            'function': self.function,
            'label': self.label
        }
    

class UsbDevice:
    def __init__(self, device_info):
        self.id = device_info['id'].decode('utf-8')
        self.path = os.path.join('/dev/bus/usb', device_info['bus'].decode('utf-8'), device_info['device'].decode('utf-8'))
        self.name = device_info['tag'].decode('utf-8')
        self.vendor_id = self.id.split(':')[0]
        self.product_id = self.id.split(':')[1]

    @property
    def json(self):
        return {
            'id': self.id,
            'path': self.path,
            'name': self.name,
            'vendor_id': self.vendor_id,
            'product_id': self.product_id,
        }


class SystemInfo:
    def __init__(self):
        self.libvirt_conn = libvirt_connection.connection
        self._cpu_model = "Unknown"
        self._motherboard = "Unknown"
        self._memory_size = 0
        self._os = "Unknown"
        self._linux_kernel = "Unknown"
        self._uptime = "Unknown"
        self._pcie_devices = []
        self._usb_devices = []
        self.libvirt_sysinfo_xml = ET.fromstring(self.libvirt_conn.getSysinfo())
        
        self.get_cpu_info()
        self.get_motherboard_info()
        self.get_memory_size()
        self.get_os_info()
        self.get_linux_kernel_info()
        self.get_uptime()
        self.get_pcie_devices()
        self.get_usb_devices()
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
    
    @property
    def pcie_devices(self):
        return self._pcie_devices
    
    @property
    def pcie_devices_json(self):
        return [device.json for device in self._pcie_devices]
    
    @property
    def usb_devices(self):
        return self._usb_devices
    
    @property
    def usb_devices_json(self):
        return [device.json for device in self._usb_devices]

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
    
    def get_pcie_devices(self):
        pcie_devices = self.libvirt_conn.listAllDevices(2)
        for device in pcie_devices:
            self._pcie_devices.append(PcieDevice(device.XMLDesc()))

        self._pcie_devices.sort(key=lambda x: x.path)

    def get_usb_devices(self):
        device_regex = re.compile(b"Bus\s+(?P<bus>\d+)\s+Device\s+(?P<device>\d+).+ID\s(?P<id>\w+:\w+)\s(?P<tag>.+)$", re.I)
        subprocess_result = subprocess.check_output(["lsusb"])
        for line in subprocess_result.split(b'\n'):
            match = device_regex.match(line)
            if match:
                usb_device = UsbDevice(match.groupdict())
                if "Linux Foundation" not in usb_device.name:
                    self._usb_devices.append(usb_device)

        