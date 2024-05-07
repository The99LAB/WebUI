from host_manager import libvirt_connection
from xml.etree import ElementTree as ET
import libvirt
from .vmManagerException import VmManagerException
from storage_manager import convertSizeUnit
from host_manager import SystemInfo, UsbDevice
import re

class VirtualMachine:
    def __init__(self, vm_uuid):
        self.vm_uuid = vm_uuid
        self.libvirt_conn = libvirt_connection.connection
        self.libvirt_domain = self.libvirt_conn.lookupByUUIDString(vm_uuid)
        self.host_system_info = SystemInfo()
        self.vm_xml = self.libvirt_domain.XMLDesc()
        self.vm_xml_root = ET.fromstring(self.vm_xml)
        self.vm_name = self.libvirt_domain.name()
        self.vm_autostart = bool(self.libvirt_domain.autostart())
        self.vm_cpu_mode = ""
        self.vm_cpu_vcpu = 0
        self.vm_cpu_current_vcpu = 0
        self.vm_cpu_custom_topology = False
        self.vm_cpu_topology_sockets = 0
        self.vm_cpu_topology_dies = 0
        self.vm_cpu_topology_cores = 0
        self.vm_cpu_topology_threads = 0
        self.vm_machine_type = ""
        self.vm_bios_type = ""
        self.vm_memory_min = 0
        self.vm_memory_min_unit = "MB"
        self.vm_memory_max = 0
        self.vm_memory_max_unit = "MB"
        self.vm_disk_devices = []
        self.vm_network_devices = []
        self.vm_sound_devices = []
        self.vm_usb_devices = []
        self.vm_pci_devices = []
        self.vm_graphics_devices = []
        self.vm_video_devices = []
        self.vm_state = ""
        self.get_vm_state()
        self.get_vm_cpu_info()
        self.get_vm_memory_info()
        self.get_vm_bios_type()
        self.get_vm_machine_type()
        self.get_vm_network_devices()
        self.get_vm_usb_devices()


    def get_vm_machine_type(self):
        self.vm_machine_type = self.vm_xml_root.find("os/type").attrib["machine"]


    def get_vm_bios_type(self):
        os_loader = self.vm_xml_root.find("os/loader")
        self.vm_bios_type = "BIOS"
        if os_loader is not None:
            self.vm_bios_type = os_loader.text

    
    def get_vm_network_devices(self):
        self.vm_network_devices = []
        network_devices = self.vm_xml_root.findall("./devices/interface")
        for number, interface in enumerate(network_devices):
            interface_xml = ET.tostring(interface).decode()
            if interface.get('type') == 'network':
                mac_address = interface.find("mac").get("address")
                source_network = self.libvirt_conn.networkLookupByName(interface.find("source").get("network")).name()
                model = interface.find("model").get("type")
                boot_element = interface.find("boot")
                boot_order = None
                if boot_element != None:
                    boot_order = boot_element.get("order")
                self.vm_network_devices.append({
                    'number': number,
                    'xml': interface_xml,
                    'mac_address': mac_address,
                    'source': source_network,
                    'model': model,
                    'boot_order': boot_order,
                })
        print(self.vm_network_devices)
    

    def remove_vm_network_device(self, number):
        for idx, interface in enumerate(self.vm_network_devices):
            if idx == int(number):
                interface_xml = interface['xml']
                try:
                    self.libvirt_domain.detachDeviceFlags(interface_xml, libvirt.VIR_DOMAIN_AFFECT_CONFIG)
                except libvirt.libvirtError as e:
                    raise VmManagerException(f"Failed to remove network device: {e}")
                break
        self.get_vm_network_devices()


    def get_vm_usb_devices(self):
        self.vm_usb_devices = []
        hostdevs = self.vm_xml_root.findall("./devices/hostdev")
        for hostdev in hostdevs:
            foundSystemUsbDevice = False
            hostdevtype = hostdev.get("type")
            if hostdevtype == "usb":
                vendor_id = hostdev.find("source/vendor").get("id").replace("0x", "")
                product_id = hostdev.find("source/product").get("id").replace("0x", "")

                for host_usb_device in self.host_system_info.usb_devices:
                    system_usb_device_product_id = str(host_usb_device.product_id)
                    system_usb_device_vendor_id = str(host_usb_device.vendor_id)
                    system_usb_device_name = host_usb_device.name

                    if system_usb_device_vendor_id == vendor_id and system_usb_device_product_id == product_id:
                        foundSystemUsbDevice = True
            
            if not foundSystemUsbDevice:
                system_usb_device_name = "Unknown"
            self.vm_usb_devices.append({
                "name": system_usb_device_name,
                "vendor_id": vendor_id,
                "product_id": product_id,
            })


    def add_vm_usb_device(self, vendor_id:int, product_id:int, hotplug=False):
        usb_device_xml = f"""
        <hostdev mode='subsystem' type='usb'>
            <source>
                <vendor id='0x{vendor_id}'/>
                <product id='0x{product_id}'/>
            </source>
        </hostdev>
        """
        try:
            if hotplug:
                self.libvirt_domain.attachDeviceFlags(usb_device_xml, libvirt.VIR_DOMAIN_AFFECT_LIVE)
            else:
                self.libvirt_domain.attachDeviceFlags(usb_device_xml, libvirt.VIR_DOMAIN_AFFECT_CONFIG)
        except libvirt.libvirtError as e:
            raise VmManagerException(f"Failed to add USB device: {e}")


    def remove_vm_usb_device(self, vendor_id:int, product_id:int, hotunplug=False):
        usb_device_xml = f"""
        <hostdev mode='subsystem' type='usb'>
            <source>
                <vendor id='0x{vendor_id}'/>
                <product id='0x{product_id}'/>
            </source>
        </hostdev>
        """
        try:
            if hotunplug:
                self.libvirt_domain.detachDeviceFlags(usb_device_xml, libvirt.VIR_DOMAIN_AFFECT_LIVE)
            else:
                self.libvirt_domain.detachDeviceFlags(usb_device_xml, libvirt.VIR_DOMAIN_AFFECT_CONFIG)
        except libvirt.libvirtError as e:
            raise VmManagerException(f"Failed to remove USB device: {e}")


    def get_vm_memory_info(self):
        domain_memory_info = self.libvirt_domain.info()
        min_memory_conversion = convertSizeUnit(size=domain_memory_info[1], from_unit="KB", mode="tuple")
        max_memory_conversion = convertSizeUnit(size=domain_memory_info[2], from_unit="KB", mode="tuple")
        self.vm_memory_min = min_memory_conversion[0]
        self.vm_memory_min_unit = min_memory_conversion[1]
        self.vm_memory_max = max_memory_conversion[0]
        self.vm_memory_max_unit = max_memory_conversion[1]


    def get_vm_cpu_info(self):
        self.vm_cpu_mode = self.vm_xml_root.find("cpu").get("mode")
        self.vm_cpu_vcpu = int(self.vm_xml_root.find("vcpu").text)
        try:
            self.vm_cpu_current_vcpu = int(self.vm_xml_root.find("vcpu").attrib["current"])
        except KeyError:
            self.vm_cpu_current_vcpu = self.vm_cpu_vcpu

        topology_xml = self.vm_xml_root.find("cpu/topology")
        if topology_xml is None:
            self.vm_cpu_custom_topology = False
            self.vm_cpu_topology_sockets = self.vm_cpu_vcpu
            self.vm_cpu_topology_dies = 1
            self.vm_cpu_topology_cores = 1
            self.vm_cpu_topology_threads = 1
        else:
            self.vm_cpu_custom_topology = True
            self.vm_cpu_topology_sockets = int(topology_xml.attrib["sockets"])
            self.vm_cpu_topology_dies = int(topology_xml.attrib["dies"])
            self.vm_cpu_topology_cores = int(topology_xml.attrib["cores"])
            self.vm_cpu_topology_threads = int(topology_xml.attrib["threads"])


    def get_vm_state(self):
        state, result = self.libvirt_domain.state()
        if state == libvirt.VIR_DOMAIN_NOSTATE:
            self.vm_state = "NOSTATE"
        elif state == libvirt.VIR_DOMAIN_RUNNING:
            self.vm_state = "RUNNING"
        elif state == libvirt.VIR_DOMAIN_BLOCKED:
            self.vm_state = "BLOCKED"
        elif state == libvirt.VIR_DOMAIN_PAUSED:
            self.vm_state = "PAUSED"
        elif state == libvirt.VIR_DOMAIN_SHUTDOWN:
            self.vm_state = "SHUTDOWN"
        elif state == libvirt.VIR_DOMAIN_SHUTOFF:
            self.vm_state = "SHUTOFF"
        elif state == libvirt.VIR_DOMAIN_CRASHED:
            self.vm_state = "CRASHED"
        elif state == libvirt.VIR_DOMAIN_PMSUSPENDED:
            self.vm_state = "PMSUSPENDED"
        else:
            self.vm_state = "UNKNOWN"


    def set_vm_autostart(self, autostart):
        self.libvirt_domain.setAutostart(autostart)
        self.vm_autostart = autostart

    def set_vm_memory(self, min_memory, max_memory, min_memory_unit, max_memory_unit):
        min_memory_kb = convertSizeUnit(size=min_memory, from_unit=min_memory_unit, to_unit="KB", mode="int")
        max_memory_kb = convertSizeUnit(size=max_memory, from_unit=max_memory_unit, to_unit="KB", mode="int")

        if min_memory_kb > max_memory_kb:
            raise VmManagerException("Minimum memory cannot be greater than maximum memory")
        else:
            try:
                current_min_memory = re.search("<currentMemory unit='KiB'>[0-9]+</currentMemory>", self.vm_xml).group()
                current_max_memory = re.search("<memory unit='KiB'>[0-9]+</memory>", self.vm_xml).group()
                try:
                    vm_xml_output = self.vm_xml
                    vm_xml_output = vm_xml_output.replace(current_min_memory, f"<currentMemory unit='KiB'>{min_memory_kb}</currentMemory>")
                    vm_xml_output = vm_xml_output.replace(current_max_memory, f"<memory unit='KiB'>{max_memory_kb}</memory>")
                    try:
                        print("Setting memory")
                        print(vm_xml_output)
                        self.libvirt_conn.defineXML(vm_xml_output)
                    except libvirt.libvirtError as e:
                        raise VmManagerException(f"Failed to set memory: {e}")
                except AttributeError:
                    raise VmManagerException("Failed to set memory: Memory not found in XML")
            except AttributeError:
                raise VmManagerException("Failed to find minimum or maximum memory in XML")

    @property
    def json(self):
        return {
            'uuid': self.vm_uuid,
            'name': self.vm_name,
            'state': self.vm_state,
            'autostart': self.vm_autostart,
            'cpu_mode': self.vm_cpu_mode,
            'vcpu': self.vm_cpu_vcpu,
            'current_vcpu': self.vm_cpu_current_vcpu,
            'cpu_custom_topology': self.vm_cpu_custom_topology,
            'cpu_topology_sockets': self.vm_cpu_topology_sockets,
            'cpu_topology_dies': self.vm_cpu_topology_dies,
            'cpu_topology_cores': self.vm_cpu_topology_cores,
            'cpu_topology_threads': self.vm_cpu_topology_threads,
            'machine_type': self.vm_machine_type,
            'bios_type': self.vm_bios_type,
            'memory_min': self.vm_memory_min,
            'memory_min_unit': self.vm_memory_min_unit,
            'memory_max': self.vm_memory_max,
            'memory_max_unit': self.vm_memory_max_unit,
            'disk_devices': [],
            'network_devices': self.vm_network_devices,
            'sound_devices': [],
            'usb_devices': self.vm_usb_devices,
            'pci_devices': [],
            'graphics_devices': [],
            'video_devices': [],
            'xml': self.vm_xml
        }
    

# Class for all virtual machines in the system
# For example used to list all virtual machines in the system
class VirtualMachines:
    def __init__(self):
        self.libvirt_conn = libvirt_connection.connection
        self.libvirt_domains = self.libvirt_conn.listAllDomains()

    @property
    def json(self):
        vms = []
        for domain in self.libvirt_domains:
            vms.append(VirtualMachine(domain.UUIDString()).json)
        return vms