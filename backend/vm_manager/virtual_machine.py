from host_manager import libvirt_connection
from xml.etree import ElementTree as ET
import libvirt
from .vmManagerException import VmManagerException
from storage_manager import convertSizeUnit
from host_manager import SystemInfo, UsbDevice
import re
import os
from string import ascii_lowercase

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
        self.vm_memory_memorybacking = False
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
        self.get_vm_sound_devices()
        self.get_vm_graphics_devices()
        self.get_vm_video_devices()
        self.get_vm_pcie_devices()
        self.get_vm_storage_devices()


    def get_vm_machine_type(self):
        self.vm_machine_type = self.vm_xml_root.find("os/type").attrib["machine"]


    def get_vm_bios_type(self):
        os_loader = self.vm_xml_root.find("os/loader")
        self.vm_bios_type = "BIOS"
        if os_loader is not None:
            self.vm_bios_type = os_loader.text


    def get_vm_storage_devices(self):
        self.vm_disk_devices = []
        disk_devices = self.vm_xml_root.findall("devices/disk")
        for index, disk_device in enumerate(disk_devices):
            xml = ET.tostring(disk_device).decode()
            disk_type = disk_device.get("type")
            device_type = disk_device.get("device")
            driver_type = disk_device.find("driver").get("type")
            boot_order_element = disk_device.find("boot")
            boot_order = None
            if boot_order_element != None:
                boot_order = boot_order_element.get("order")

            source_element = disk_device.find("source")
            source_file = None
            source_device = None
            if source_element is not None:
                source_file = source_element.get("file")
                source_device = source_element.get("dev")

            target_element = disk_device.find("target")
            bus_format = target_element.get("bus")
            target_device = target_element.get("dev")

            read_only_element = disk_device.find("readonly")
            read_only = False
            if read_only_element is not None:
                read_only = True
           
            disk_device = {
                "index": index,
                "xml": xml,
                "disk_type": disk_type,
                "device_type": device_type,
                "driver_type": driver_type,
                "bus_format": bus_format,
                "source_file": source_file,
                "source_device": source_device,
                "target_device": target_device,
                "read_only": read_only,
                "boot_order": boot_order,
            }
            self.vm_disk_devices.append(disk_device)


    def remove_vm_storage_device(self, index:int):
        disk_device = next((disk_device for disk_device in self.vm_disk_devices if disk_device["index"] == int(index)), None)
        if disk_device is None:
            raise VmManagerException(f"Failed to remove disk device: Disk device with number {index} not found")
        disk_device_xml = disk_device["xml"]
        try:
            self.libvirt_domain.detachDeviceFlags(disk_device_xml, libvirt.VIR_DOMAIN_AFFECT_CONFIG)
        except libvirt.libvirtError as e:
            raise VmManagerException(f"Failed to remove disk device with index {index}: {e}")
        self.get_vm_storage_devices()


    def _add_vm_storage_device(self, disk_type:str, disk_bus:str, device_type:str, source_file:None, source_device:None):
        print(source_file, disk_bus, device_type)
        if disk_type not in ["file", "block"]:
            raise VmManagerException("Failed to add disk device: Invalid disk type specified")
        if device_type not in ["disk", "cdrom"]:
            raise VmManagerException("Failed to add disk device: Invalid device type specified")
        if disk_bus not in ["ide", "scsi", "virtio", "sata"]:
            raise VmManagerException("Failed to add disk device: Invalid disk bus specified")
        if disk_type == 'file':
            if not os.path.isfile(source_file):
                raise VmManagerException("Failed to add disk device: Source file does not exist")
        elif disk_type == 'block':
            if not os.path.exists(source_device):
                raise VmManagerException("Failed to add disk device: Source device does not exist")

        # calculate the next available target device
        target_devices = [disk_device["target_device"] for disk_device in self.vm_disk_devices]
        last_used_target_device = None
        new_target_device = None
        for target_device in target_devices:
            if disk_bus == "sata" or disk_bus == "scsi" or disk_bus == "usb":
                if target_device.startswith("sd"):
                    last_used_target_device = target_device.replace("sd", "")
            elif disk_bus == "virtio":
                if target_device.startswith("vd"):
                    last_used_target_device = target_device.replace("vd", "")

        try:
            index = ascii_lowercase.index(last_used_target_device)+1
        except TypeError:
            index = 0
        if disk_bus == "sata" or disk_bus == "scsi" or disk_bus == "usb":
            new_target_device = f"sd{ascii_lowercase[index]}"
        elif disk_bus == "virtio":
            new_target_device = f"vd{ascii_lowercase[index]}"

        driver_type = "raw"
        if source_file.endswith(".qcow2"):
            driver_type = "qcow2"
        
        disk_device_xml = f"""
        <disk type='{disk_type}' device='{device_type}'>
            <driver name='qemu' type='{driver_type}'/>
            <source {f"file='{source_file}'" if source_file else f"dev='{source_device}'"}/>
            <target dev='{new_target_device}' bus='{disk_bus}'/>
        </disk>
        """
        print(disk_device_xml)
        try:
            self.libvirt_domain.attachDeviceFlags(disk_device_xml, libvirt.VIR_DOMAIN_AFFECT_CONFIG)
        except libvirt.libvirtError as e:
            raise VmManagerException(f"Failed to add disk device: {e}")


    def add_vm_storage_device_from_file(self, disk_bus:str, device_type:str, source_file:str):
        self._add_vm_storage_device(disk_type="file", disk_bus=disk_bus, device_type=device_type, source_file=source_file, source_device=None)


    def add_vm_storage_device_from_block_device(self, disk_bus:str, source_device:str):
        self._add_vm_storage_device(disk_type="block", disk_bus=disk_bus, device_type='disk', source_device=source_device, source_file=None)


    def get_vm_network_devices(self):
        self.vm_network_devices = []
        network_devices = self.vm_xml_root.findall("devices/interface")
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


    def remove_vm_network_device(self, number):
        network_interface = next((network_device for network_device in self.vm_network_devices if network_device["number"] == int(number)), None)
        if network_interface is None:
            raise VmManagerException(f"Failed to remove network device: Network device with number {number} not found")
        network_interface_xml = network_interface["xml"]
        try:
            self.libvirt_domain.detachDeviceFlags(network_interface_xml, libvirt.VIR_DOMAIN_AFFECT_CONFIG)
        except libvirt.libvirtError as e:
            raise VmManagerException(f"Failed to remove network device: {e}")
        self.get_vm_network_devices()


    def add_vm_network_device(self, source_network_uuid:str, model_type:str, mac_address:str=""):
        if model_type not in ["virtio", "e1000", "rtl8139"]:
            raise VmManagerException("Failed to add network device: Invalid network device model specified")
        try:
            source_network_name = self.libvirt_conn.networkLookupByUUIDString(source_network_uuid).name()
        except libvirt.libvirtError as e:
            raise VmManagerException(f"Failed to add network device: could not find network with UUID {source_network_uuid}")
        network_interface_xml = f"""
        <interface type='network'>
            <source network='{source_network_name}'/>
            <model type='{model_type}'/>
            {f"<mac address='{mac_address}'/>" if mac_address else ""}
        </interface>
        """
        try:
            self.libvirt_domain.attachDeviceFlags(network_interface_xml, libvirt.VIR_DOMAIN_AFFECT_CONFIG)
        except libvirt.libvirtError as e:
            raise VmManagerException(f"Failed to add network device: {e}")


    def get_vm_pcie_devices(self):
        self.vm_pci_devices = []
        pci_devices = self.vm_xml_root.findall("devices/hostdev")
        for index, pci_device in enumerate(pci_devices):
            foundSystemPciDevice = False
            hostdevtype = pci_device.get("type")
            if hostdevtype == "pci":
                xml = ET.tostring(pci_device).decode()
                source_address = pci_device.find("source/address")
                domain = str(hex(int(source_address.get("domain"), 0))).replace("0x", "")
                bus = str(hex(int(source_address.get("bus"), 0))).replace("0x", "")
                slot = str(hex(int(source_address.get("slot"), 0))).replace("0x", "")
                function = str(hex(int(source_address.get("function"), 0))).replace("0x", "")
                rom_element = pci_device.find("rom")
                rom_file = ""
                custom_rom = False
                if rom_element is not None:
                    rom_file = rom_element.get("file")
                    custom_rom = True
                
                for host_pci_device in self.host_system_info.pcie_devices:
                    system_pci_device_domain = host_pci_device.domain
                    system_pci_device_bus = host_pci_device.bus
                    system_pci_device_slot = host_pci_device.slot
                    system_pci_device_function = host_pci_device.function
                    pci_device_product_name = host_pci_device.product_name
                    pci_device_vendor_name = host_pci_device.vendor_name
                    pci_device_path = host_pci_device.path

                    if system_pci_device_domain == domain and system_pci_device_bus == bus and system_pci_device_slot == slot and system_pci_device_function == function:
                        foundSystemPciDevice = True
                        break

                if not foundSystemPciDevice:
                    pci_device_path = "Unknown"
                    pci_device_vendor_name = "Unknown"
                    pci_device_product_name = "Unknown"

                self.vm_pci_devices.append({
                    "index": index,
                    "xml": xml,
                    "path": pci_device_path,
                    "domain": domain,
                    "bus": bus,
                    "slot": slot,
                    "function": function,
                    "rom_file": rom_file,
                    "custom_rom_file": custom_rom,
                    "vendor_name": pci_device_vendor_name,
                    "product_name": pci_device_product_name,
                })


    def remove_vm_pcie_device(self, index:int):
        pci_device = next((pci_device for pci_device in self.vm_pci_devices if pci_device["index"] == int(index)), None)
        if pci_device is None:
            raise VmManagerException(f"Failed to remove PCI device: PCI device with number {index} not found")
        pci_device_xml = pci_device["xml"]
        try:
            self.libvirt_domain.detachDeviceFlags(pci_device_xml, libvirt.VIR_DOMAIN_AFFECT_CONFIG)
        except libvirt.libvirtError as e:
            raise VmManagerException(f"Failed to remove PCI device: {e}")
        self.get_vm_pcie_devices()


    def add_vm_pcie_device(self, domain:str, bus:str, slot:str, function:str, rom_file:str, custom_rom:bool):
        pci_device_xml = f"""
        <hostdev mode='subsystem' type='pci' managed='yes'>
            <source>
                <address domain='0x{domain}' bus='0x{bus}' slot='0x{slot}' function='0x{function}'/>
            </source>
            {f"<rom file='{rom_file}'/>" if custom_rom else ""}
        </hostdev>
        """
        try:
            self.libvirt_domain.attachDeviceFlags(pci_device_xml, libvirt.VIR_DOMAIN_AFFECT_CONFIG)
        except libvirt.libvirtError as e:
            raise VmManagerException(f"Failed to add PCI device: {e}")


    def get_vm_graphics_devices(self):
        self.vm_graphics_devices = []
        graphics_devices = self.vm_xml_root.findall("devices/graphics")
        for index, graphics_device in enumerate(graphics_devices):
            xml = ET.tostring(graphics_device).decode()
            graphics_type = graphics_device.get("type")
            self.vm_graphics_devices.append({
                "index": index,
                "type": graphics_type,
            })


    def remove_vm_graphics_device(self, index:int):
        graphics_element = self.vm_xml_root.find(f"devices/graphics[{index+1}]")
        if graphics_element is None:
            raise VmManagerException(f"Failed to remove graphics device: Graphics device with number {index} not found")
        # Remove everything inside the graphics element
        for child in graphics_element:
            graphics_element.remove(child)
        # Remove all attributes from the graphics element
        graphics_element.attrib.clear()
        # Remove the graphics element itself
        self.vm_xml_root.find("devices").remove(graphics_element)
        try:
            self.libvirt_conn.defineXML(ET.tostring(self.vm_xml_root).decode())
        except libvirt.libvirtError as e:
            raise VmManagerException(f"Failed to remove graphics device: {e}")


    def add_vm_graphics_device(self, graphics_type):
        if graphics_type not in ["vnc", "spice"]:
            raise VmManagerException("Failed to add graphics device: Invalid graphics device type specified")
        graphics_element =  ET.fromstring(f"<graphics type='{graphics_type}'/>")
        self.vm_xml_root.find("devices").append(graphics_element)
        try:
            self.libvirt_conn.defineXML(ET.tostring(self.vm_xml_root).decode())
        except libvirt.libvirtError as e:
            raise VmManagerException(f"Failed to add graphics device: {e}")


    def get_vm_video_devices(self):
        self.vm_video_devices = []
        video_devices = self.vm_xml_root.findall("devices/video")
        for index, video_device in enumerate(video_devices):
            xml = ET.tostring(video_device).decode()
            model_type = video_device.find("model").attrib["type"]
            self.vm_video_devices.append({
                "index": index,
                "type": model_type,
            })


    def remove_vm_video_device(self, index:int):
        # Note: we cannot use detachDeviceFlags as it is not supported for video devices
        video_element = self.vm_xml_root.find(f"devices/video[{index+1}]")
        if video_element is None:
            raise VmManagerException(f"Failed to remove video device: Video device with number {index} not found")
        # Remove everything inside the video element
        for child in video_element:
            video_element.remove(child)
        # Remove all attributes from the video element
        video_element.attrib.clear()
        # Remove the video element itself
        self.vm_xml_root.find("devices").remove(video_element)
        try:
            self.libvirt_conn.defineXML(ET.tostring(self.vm_xml_root).decode())
        except libvirt.libvirtError as e:
            raise VmManagerException(f"Failed to remove video device: {e}")


    def add_vm_video_device(self, model_type):
        # Note: we cannot use attachDeviceFlags as it is not supported for video devices
        if model_type not in ["qxl", "vga", "virtio"]:
            raise VmManagerException("Failed to add video device: Invalid video device model specified")
        video_element =  ET.fromstring(f"<video><model type='{model_type}'/></video>")
        self.vm_xml_root.find("devices").append(video_element)
        try:
            self.libvirt_conn.defineXML(ET.tostring(self.vm_xml_root).decode())
        except libvirt.libvirtError as e:
            raise VmManagerException(f"Failed to add video device: {e}")


    def get_vm_sound_devices(self):
        self.vm_sound_devices = []
        sound_devices = self.vm_xml_root.findall("devices/sound")
        for index, sound_device in enumerate(sound_devices):
            xml = ET.tostring(sound_device).decode()
            model = sound_device.get("model")
            self.vm_sound_devices.append({
                "index": index,
                "xml": xml,
                "model": model,
            })


    def remove_vm_sound_device(self, index:int):
        sound_device = next((sound_device for sound_device in self.vm_sound_devices if sound_device["index"] == int(index)), None)
        if sound_device is None:
            raise VmManagerException(f"Failed to remove sound device: Sound device with number {index} not found")
        sound_device_xml = sound_device["xml"]
        try:
            self.libvirt_domain.detachDeviceFlags(sound_device_xml, libvirt.VIR_DOMAIN_AFFECT_CONFIG)
        except libvirt.libvirtError as e:
            raise VmManagerException(f"Failed to remove sound device: {e}")        
        self.get_vm_sound_devices()


    def add_vm_sound_device(self, model):
        if model not in ["ac97", "ich6", "ich9"]:
            raise VmManagerException("Invalid audio model specified")
        sound_element = f"<sound model='{model}'/>"
        try:
            self.libvirt_domain.attachDeviceFlags(sound_element, libvirt.VIR_DOMAIN_AFFECT_CONFIG)
        except libvirt.libvirtError as e:
            raise VmManagerException(f"Failed to add audio device: {e}")


    def get_vm_usb_devices(self):
        self.vm_usb_devices = []
        hostdevs = self.vm_xml_root.findall("devices/hostdev")
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


    def generate_vm_usb_device_xml(self, vendor_id:int, product_id:int):
        usb_device_xml = f"""
        <hostdev mode='subsystem' type='usb'>
            <source>
                <vendor id='0x{vendor_id}'/>
                <product id='0x{product_id}'/>
            </source>
        </hostdev>
        """
        return usb_device_xml


    def add_vm_usb_device(self, vendor_id:int, product_id:int, hotplug=False):
        usb_device_xml = self.generate_vm_usb_device_xml(vendor_id, product_id)
        try:
            if hotplug:
                self.libvirt_domain.attachDeviceFlags(usb_device_xml, libvirt.VIR_DOMAIN_AFFECT_LIVE)
            else:
                self.libvirt_domain.attachDeviceFlags(usb_device_xml, libvirt.VIR_DOMAIN_AFFECT_CONFIG)
        except libvirt.libvirtError as e:
            raise VmManagerException(f"Failed to add USB device with vendor_id: {vendor_id} and product_id: {product_id} to VM: {e}")


    def remove_vm_usb_device(self, vendor_id:int, product_id:int, hotunplug=False):
        usb_device_xml = self.generate_vm_usb_device_xml(vendor_id, product_id)
        try:
            if hotunplug:
                self.libvirt_domain.detachDeviceFlags(usb_device_xml, libvirt.VIR_DOMAIN_AFFECT_LIVE)
            else:
                self.libvirt_domain.detachDeviceFlags(usb_device_xml, libvirt.VIR_DOMAIN_AFFECT_CONFIG)
        except libvirt.libvirtError as e:
            raise VmManagerException(f"Failed to remove USB device with vendor_id: {vendor_id} and product_id: {product_id} from VM: {e}")


    def get_vm_memory_info(self):
        try:
            domain_memory_info = self.libvirt_domain.info()
        except libvirt.libvirtError as e:
            raise VmManagerException(f"Failed to get memory info: {e}")
        min_memory_conversion = convertSizeUnit(size=domain_memory_info[1], from_unit="KB", mode="tuple")
        max_memory_conversion = convertSizeUnit(size=domain_memory_info[2], from_unit="KB", mode="tuple")
        self.vm_memory_min = min_memory_conversion[0]
        self.vm_memory_min_unit = min_memory_conversion[1]
        self.vm_memory_max = max_memory_conversion[0]
        self.vm_memory_max_unit = max_memory_conversion[1]

        memory_backing = self.vm_xml_root.find("memoryBacking")
        if memory_backing is not None:
            self.vm_memory_memorybacking = True
        else:
            self.vm_memory_memorybacking = False


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


    def set_vm_memory(self, min_memory, max_memory, min_memory_unit, max_memory_unit, memory_backing=False):
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
                except AttributeError:
                    raise VmManagerException("Failed to set memory: Memory not found in XML")
                
                # Enable or disable memory backing
                vm_xml_output = ET.fromstring(vm_xml_output)
                memory_backing_element = vm_xml_output.find("memoryBacking")
                if memory_backing:
                    if memory_backing_element is None:
                        memory_backing_element_new = ET.fromstring(f"""
                            <memoryBacking>
                                <source type='memfd'/>
                                <access mode='shared'/>
                            </memoryBacking> 
                            """)
                        vm_xml_output.append(memory_backing_element_new)
                else:
                    if memory_backing_element is not None:
                        vm_xml_output.remove(memory_backing_element)

                try:
                    self.libvirt_conn.defineXML(ET.tostring(vm_xml_output).decode())
                except libvirt.libvirtError as e:
                    raise VmManagerException(f"Failed to set memory: {e}")
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
            'memory_enable_shared': self.vm_memory_memorybacking,
            'disk_devices': self.vm_disk_devices,
            'network_devices': self.vm_network_devices,
            'sound_devices': self.vm_sound_devices,
            'usb_devices': self.vm_usb_devices,
            'pci_devices': self.vm_pci_devices,
            'graphics_devices': self.vm_graphics_devices,
            'video_devices': self.vm_video_devices,
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