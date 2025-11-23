"""
VM Service - Handles libvirt operations for virtual machines
Separates business logic from data models
"""
from .VmException import VmException
from .vmbasic import VirtualMachineBasic, VirtualMachineBasicBiosTypes
from host_manager import libvirt_connection
import libvirt
import os
import time


class VmService:
    """Service class for VM libvirt operations"""
    
    def __init__(self, vm: VirtualMachineBasic):
        self.vm = vm
        self.conn = libvirt_connection.connection

    def gen_graphics(self):
        return f"""<graphics type='spice' port='-1' autoport='yes'><listen type='address' address='127.0.0.1'/> </graphics>"""
    
    def gen_video(self):
        return f"""<video><model type='{self.vm.video_type}'/> </video>"""
    
    def gen_loader(self):
        if self.vm.bios_type == VirtualMachineBasicBiosTypes.OVMF:
            nvram_path = "/mnt/data/s99-vmb-vars/"
            if not os.path.exists(nvram_path):
                os.makedirs(nvram_path)
            nvram_path += f"{self.vm.id}.fd"
            return f"""<loader readonly='yes' type='pflash'>{self.vm.ovmf_path.path}</loader>
            <nvram>{nvram_path}</nvram>"""
        else:
            return ""
        
    def gen_devices_disk_file(self):
        devices_disk_file = ""
        for index, device in enumerate(self.vm.devices_disk_file):
            targetdev = "sd"
            targetdev += chr(ord("a") + index)
            drivertype = "raw"
            if device.disk_source_file.endswith(".qcow2"):
                drivertype = "qcow2"
            devices_disk_file += f"""<disk type='file' device='{device.device_type}'>
            <driver name='qemu' type='{drivertype}'/>
            <source file='{device.disk_source_file}'/>
            <target dev='{targetdev}' bus='{device.disk_bus}'/>
            </disk>"""
        print(devices_disk_file)
        return devices_disk_file
    
    def gen_devices_disk_block(self):
        devices_disk_block = ""
        # Calculate starting index based on number of file disks
        start_index = len(self.vm.devices_disk_file)
        for index, device in enumerate(self.vm.devices_disk_block):
            targetdev = "sd"
            targetdev += chr(ord("a") + start_index + index)
            devices_disk_block += f"""<disk type='block' device='{device.device_type}'>
            <driver name='qemu' type='raw'/>
            <source dev='{device.disk_source_block}'/>
            <target dev='{targetdev}' bus='{device.disk_bus}'/>
            </disk>"""
        return devices_disk_block
    
    def gen_devices_disk_iscsi(self):
        devices_disk_iscsi = ""
        # Calculate starting index based on number of file and block disks
        start_index = len(self.vm.devices_disk_file) + len(self.vm.devices_disk_block)
        for index, device in enumerate(self.vm.devices_disk_iscsi):
            targetdev = "sd"
            targetdev += chr(ord("a") + start_index + index)
            devices_disk_iscsi += f"""<disk type='network' device='{device.device_type}'>
            <driver name='qemu' type='raw'/>
            <source protocol='iscsi' name='{device.iscsi_name}'>
              <host name='{device.iscsi_host}' port='{device.iscsi_port}'/>
            </source>
            <target dev='{targetdev}' bus='{device.disk_bus}'/>
            </disk>"""
        return devices_disk_iscsi
    
    def gen_devices_pci(self):
        devices_pci = ""
        for device in self.vm.devices_pci:
            rom_section = ""
            if device.rom_use and device.rom_file:
                rom_section = f"<rom file='{device.rom_file}'/>"
            devices_pci += f"""<hostdev mode='subsystem' type='pci' managed='yes'>
            <source>
                <address domain='0x{device.domain}' bus='0x{device.bus}' slot='0x{device.slot}' function='0x{device.function}'/>
            </source>
            {rom_section}
        </hostdev>"""
        return devices_pci
    
    def gen_devices_network(self):
        devices_network = ""
        for index, device in enumerate(self.vm.devices_network):
            if device.mac:
                devices_network += f"""<interface type='network'>
                <mac address='{device.mac}'/>
                <source network='{device.libvirt_name}'/>
                <model type='{device.type}'/>
                </interface>"""
            else:
                devices_network += f"""<interface type='network'>
                <source network='{device.libvirt_name}'/>
                <model type='{device.type}'/>
                </interface>"""
        return devices_network

    def gen_xml(self):
        xml = None
        xml = self.vm.xml_template.content.split("\n")
        xml = "".join(xml)
        xml = xml.replace("{%name%}", f"s99b-{self.vm.id}")
        xml = xml.replace("{%cpu_model%}", self.vm.cpu_model)
        xml = xml.replace("{%vcpu%}", str(self.vm.vcpu))
        xml = xml.replace("{%vcpu_current%}", str(self.vm.vcpu_current))
        xml = xml.replace("{%memory_min%}", str(self.vm.memory_min))
        xml = xml.replace("{%memory_max%}", str(self.vm.memory_max))
        xml = xml.replace("{%machine_type%}", self.vm.machine_type)
        xml = xml.replace("{%loader%}", self.gen_loader())
        xml = xml.replace("{%qemu_path%}", "/usr/bin/qemu-system-x86_64")
        xml = xml.replace("{%devices_disk_file%}", self.gen_devices_disk_file())
        xml = xml.replace("{%devices_disk_block%}", self.gen_devices_disk_block())
        xml = xml.replace("{%devices_disk_iscsi%}", self.gen_devices_disk_iscsi())
        xml = xml.replace("{%devices_pci%}", self.gen_devices_pci())
        xml = xml.replace("{%devices_network%}", self.gen_devices_network())
        xml = xml.replace("{%graphics%}", self.gen_graphics())
        xml = xml.replace("{%video%}", self.gen_video())
        # print(xml)
        return xml

    def get_libvirt_domain(self):
        return self.conn.lookupByName(f"s99b-{self.vm.id}")
    
    def start(self):
        xml = self.gen_xml()
        try:
            try:
                self.get_libvirt_domain()
                self.remove()
            except libvirt.libvirtError as e:
                pass
            self.conn.defineXML(xml)
            libvirt_domain = self.get_libvirt_domain()
            libvirt_domain.create()
        except libvirt.libvirtError as e:
            self.remove()
            raise VmException(e)

    def shutdown(self):
        libvirt_domain = self.get_libvirt_domain()
        if libvirt_domain.isActive():
            print("Shutting down VM")
            libvirt_domain.shutdown() # send shutdown signal
            # wait up to 30 seconds for the VM to shutdown
            # if the VM is still running after 30 seconds, force stop it
            for i in range(30):
                if libvirt_domain.isActive():
                    time.sleep(1)
                else:
                    print("VM has been shutdown")
                    break
        self.remove()

    def forcestop(self):
        self.remove()

    def reset(self):
        libvirt_domain = self.get_libvirt_domain()
        libvirt_domain.reset()

    def get_status(self):
        try:
            libvirt_domain = self.get_libvirt_domain()
            vm_state = None
            state, result = libvirt_domain.state()
            if state == libvirt.VIR_DOMAIN_RUNNING:
                vm_state = "Running"
            elif state == libvirt.VIR_DOMAIN_PAUSED:
                vm_state = "Paused"
            elif state == libvirt.VIR_DOMAIN_SHUTDOWN:
                vm_state = "Shutdown"
            elif state == libvirt.VIR_DOMAIN_SHUTOFF:
                vm_state = "Shutoff"
            elif state == libvirt.VIR_DOMAIN_CRASHED:
                vm_state = "Crashed"
            elif state == libvirt.VIR_DOMAIN_PMSUSPENDED:
                vm_state = "Pmsuspended"
            else:
                vm_state = "Unknown"
            return vm_state
        except libvirt.libvirtError as e:
            return "Shutoff"

    def remove(self):
        try:
            libvirt_domain = self.get_libvirt_domain()
            if libvirt_domain.isActive():
                libvirt_domain.destroy()
            libvirt_domain.undefineFlags(4)
        except libvirt.libvirtError as e:
            pass
