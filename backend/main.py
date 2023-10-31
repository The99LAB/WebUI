from fastapi import FastAPI, WebSocket, Request, Form, WebSocketDisconnect, HTTPException, Depends
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import psutil
import asyncio
import libvirt
from fastapi.middleware.cors import CORSMiddleware
from xml.etree import ElementTree as ET
import re
import os
from string import ascii_lowercase
import subprocess
import distro
import requests
import pam
import sqlite3
import select
import termios
import struct
import fcntl
import select
import signal
from jose import JWTError, jwt
from datetime import datetime, timedelta
import humanize
import json
import pwd
import grp
import shutil
import storage_manager
from notifications import NotificationManager, NotificationType, NotificationTimeType
import vm_backups
from docker_manager import Templates, Containers, Networks, Images, General


origins = ["*"]

app = FastAPI()
# app.mount("/static", StaticFiles(directory="static"), name="static")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SECRET_KEY = "secret!"
ALGORITHM = "HS256"


fd = None
child_pid = None
system_status = 'running'
conn = libvirt.open('qemu:///system')
notification_manager = NotificationManager()
vm_backup_manager = vm_backups.BackupJobManager()
dockerTemplates = Templates()
dockerContainers = Containers()
dockerNetworks = Networks()
dockerImages = Images()
dockerGeneral = General()

# check if the user is authenticated
def check_auth(request: Request):
    try:
        token = request.headers['Authorization'].split(" ")[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("username")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid authentication token")
        # check expiration
        expires = payload.get("exp")
        if expires is None:
            raise HTTPException(status_code=401, detail="Invalid authentication token")
        expires_datetime = datetime.utcfromtimestamp(expires)
        if datetime.utcnow() > expires_datetime:
            raise HTTPException(status_code=401, detail="Authentication token expired")
        return username
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication token")

# check auth by token
def check_auth_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("username")
        if username is None:
            return False
        expires = payload.get("exp")
        if expires is None:
            return False
        expires_datetime = datetime.utcfromtimestamp(expires)
        if datetime.utcnow() > expires_datetime:
            return False
        return True
    except JWTError:
        return False

def getvmstate(uuid):
    domain = conn.lookupByUUIDString(uuid)
    state, reason = domain.state()
    if state == libvirt.VIR_DOMAIN_NOSTATE:
        dom_state = 'NOSTATE'
    elif state == libvirt.VIR_DOMAIN_RUNNING:
        dom_state = 'Running'
    elif state == libvirt.VIR_DOMAIN_BLOCKED:
        dom_state = 'Blocked'
    elif state == libvirt.VIR_DOMAIN_PAUSED:
        dom_state = 'Paused'
    elif state == libvirt.VIR_DOMAIN_SHUTDOWN:
        dom_state = 'Shutdown'
    elif state == libvirt.VIR_DOMAIN_SHUTOFF:
        dom_state = 'Shutoff'
    elif state == libvirt.VIR_DOMAIN_CRASHED:
        dom_state = 'Crashed'
    elif state == libvirt.VIR_DOMAIN_PMSUSPENDED:
        dom_state = 'Pmsuspended'
    else:
        dom_state = 'unknown'
    return dom_state

def getvmresults():
    domains = conn.listAllDomains(0)
    if len(domains) != 0:
        results = []
        for domain in domains:
            dom_name = domain.name()
            dom_uuid = domain.UUIDString()
            dom_state = getvmstate(dom_uuid)
            vmXml = domain.XMLDesc(0)
            root = ET.fromstring(vmXml)
            vcpus = root.find('vcpu').text

            vnc_state = False
            if domain.isActive() == True:
                graphics = root.find('./devices/graphics')
                if graphics != None:
                    port = graphics.get('port')
                    if port != None:
                        vnc_state = True

            dom_memory_min = storage_manager.convertSizeUnit(size=vmmemory(dom_uuid).current()[0], from_unit="KB", mode="tuple")
            dom_memory_max = storage_manager.convertSizeUnit(size=vmmemory(dom_uuid).current()[1], from_unit="KB", mode="tuple")

            dom_autostart = False
            if domain.autostart() == 1:
                dom_autostart = True
            result = {
                "uuid": dom_uuid,
                "name": dom_name,
                "memory_min": dom_memory_min[0],
                "memory_min_unit": dom_memory_min[1],
                "memory_max": dom_memory_max[0],
                "memory_max_unit": dom_memory_max[1],
                "vcpus": vcpus,
                "state": dom_state,
                "VNC": vnc_state,
                "autostart": dom_autostart,
            }
            results.append(result)
    else:
        results = None
    return results


class vmmemory():
    def __init__(self, uuid):
        self.domain = conn.lookupByUUIDString(uuid)

    def current(self):
        maxmem = self.domain.info()[1]
        minmem = self.domain.info()[2]
        return [minmem, maxmem]

    def edit(self, minmem, minmemunit, maxmem, maxmemunit):
        maxmem = storage_manager.convertSizeUnit(size=maxmem, from_unit=maxmemunit, to_unit="KB", mode="int")
        minmem = storage_manager.convertSizeUnit(size=minmem, from_unit=minmemunit, to_unit="KB", mode="int")

        if minmem > maxmem:
            return ("Error: minmemory can't be bigger than maxmemory")

        else:
            vmXml = self.domain.XMLDesc(0)
            try:
                currentminmem = (
                    re.search("<currentMemory unit='KiB'>[0-9]+</currentMemory>", vmXml).group())
                currentmaxmem = (
                    re.search("<memory unit='KiB'>[0-9]+</memory>", vmXml).group())
                try:
                    output = vmXml
                    output = output.replace(
                        currentmaxmem, "<memory unit='KiB'>" + str(maxmem) + "</memory>")
                    output = output.replace(
                        currentminmem, "<currentMemory unit='KiB'>" + str(minmem) + "</currentMemory>")
                    try:
                        conn.defineXML(output)
                        return ('Succeed')
                    except libvirt.libvirtError as e:
                        return (f'Error:{e}')
                except:
                    return ("failed to replace minmemory and/or maxmemory!")
            except:
                return ("failed to find minmemory and maxmemory in xml!")


class storage():
    def __init__(self, domain_uuid):
        self.domain_uuid = domain_uuid
        self.domain = conn.lookupByUUIDString(domain_uuid)
        self.vmXml = self.domain.XMLDesc(0)

    def get(self):
        tree = ET.fromstring(self.vmXml)
        disks = tree.findall('./devices/disk')
        disklist = []
        for index, i in enumerate(disks):
            disktype = i.get('type')
            devicetype = i.get('device')
            drivertype = i.find('./driver').get('type')
            bootorderelem = i.find('boot')
            if bootorderelem != None:
                bootorder = bootorderelem.get('order')
            else:
                bootorder = None

            source = i.find('./source')
            sourcefile = None
            sourcedev = None
            if source != None:
                sourcefile = source.get('file')
                sourcedev = source.get('dev')

            target = i.find('./target')
            busformat = target.get('bus')
            targetdev = target.get('dev')
            

            readonlyelem = i.find('./readonly')
            if readonlyelem != None:
                readonly = True
            else:
                readonly = False
            disknumber = index
            xml = ET.tostring(i).decode()
            disk = {
                "number": disknumber,
                "type": disktype,
                "devicetype": devicetype,
                "drivertype": drivertype,
                "busformat": busformat,
                "sourcefile": sourcefile,
                "sourcedev": sourcedev,
                "targetdev": targetdev,
                "readonly": readonly,
                "bootorder": bootorder,
                "xml": xml
            }
            disklist.append(disk)
        return disklist

    def getxml(self, disknumber):
        return self.get()[int(disknumber)]["xml"]

    def add_xml(self, disktype, targetbus, devicetype, drivertype, sourcefile=None, sourcedev=None, bootorder=None):
        tree = ET.fromstring(self.vmXml)
        disks = tree.findall('./devices/disk')

        # get last used target bus
        for i in disks:
            target = i.find('./target')
            if targetbus == "sata" or targetbus == "scsi" or targetbus == "usb":
                if target.get('dev').startswith("sd"):
                    busformat = target.get('dev')
                    LastUsedTargetDev = busformat.replace("sd", "")
            elif targetbus == "virtio":
                if target.get('dev').startswith("vd"):
                    busformat = target.get('dev')
                    LastUsedTargetDev = busformat.replace("vd", "")

        # check which bus is free
        try:
            index = ascii_lowercase.index(LastUsedTargetDev)+1
        except NameError:
            index = 0
        if targetbus == "sata" or targetbus == "scsi" or targetbus == "usb":
            FreeTargetDev = "sd" + ascii_lowercase[index]
        elif targetbus == "virtio":
            FreeTargetDev = "vd" + ascii_lowercase[index]

        # create boot order string
        bootorderstring = ""
        if bootorder != None:
            bootorderstring = f"<boot order='{str(bootorder)}'/>"

        source_file_string = ""
        source_dev_string = ""
        if disktype == "file":
            source_file_string = f"<source file='{sourcefile}'/>"
        elif disktype == "block":
            source_dev_string = f"<source dev='{sourcedev}'/>"
        else:
            return
        # add the disk to xml
        self.diskxml = f"""<disk type='{disktype}' device='{devicetype}'>
        <driver name='qemu' type='{drivertype}'/>
        {source_file_string if disktype == "file" else ''}
        {source_dev_string if disktype == "block" else ''}
        <target dev='{FreeTargetDev}' bus='{targetbus}'/>
        {bootorderstring}
        </disk>"""

        self.add_xml_to_vm()
        return self.diskxml

    def add_xml_to_vm(self):
        self.domain.attachDeviceFlags(self.diskxml, libvirt.VIR_DOMAIN_AFFECT_CONFIG)

    def createnew(self, directory, disksize, disksizeunit, disktype, diskbus):
        disksize = storage_manager.convertSizeUnit(size=int(disksize), from_unit=disksizeunit, to_unit="B", mode="int")
        available_disk_number = len(self.get())
        disk_path = os.path.join(directory, f"{self.domain.name()}-{available_disk_number}.{disktype}")
        try:
            subprocess.check_output(["qemu-img", "create", "-f", disktype, disk_path, f"{disksize}B"])
        except subprocess.CalledProcessError as e:
            raise Exception(f"Error: Creating disk failed with error: {e}")
        self.add_xml(
            disktype="file",
            devicetype="disk",
            targetbus=diskbus,
            drivertype=disktype,
            sourcefile=disk_path,
        )


def SystemUsbDevicesList():
    device_re = re.compile(b"Bus\s+(?P<bus>\d+)\s+Device\s+(?P<device>\d+).+ID\s(?P<id>\w+:\w+)\s(?P<tag>.+)$", re.I)
    df = subprocess.check_output("lsusb")
    devices = []
    for i in df.split(b'\n'):
        if i:
            info = device_re.match(i)
            if info:
                dinfo = info.groupdict()
                dinfo['path'] = '/dev/bus/usb/%s/%s' % (dinfo.pop('bus').decode('utf-8'), dinfo.pop('device').decode('utf-8'))
                dinfo['name'] = dinfo['tag'].decode('utf-8')
                dinfo.pop('tag')
                dinfo['id'] = dinfo['id'].decode('utf-8')
                dinfo['vendorid'] = dinfo['id'].split(':')[0]
                dinfo['productid'] = dinfo['id'].split(':')[1]
                if not 'Linux Foundation' in dinfo['name']:
                    devices.append(dinfo)
    return devices


def HostPcieDevices():
    pci_devices = conn.listAllDevices(2)
    pcidevicesList = []
    for device in pci_devices:
        devicexml = device.XMLDesc()
        try:
            root = ET.fromstring(devicexml)
            path = root.find('name').text.replace('pci_', '').replace('_', ':')
            product = root.find('./capability/product')
            productid = product.get('id')
            productName = product.text
            if productName == None:
                productName = "Unknown"
            if productName == None:
                productName = ""
            vendor = root.find('./capability/vendor')
            vendorid = vendor.get('id')
            vendorName = vendor.text
            iommuGroup = root.find('./capability/iommuGroup').get('number')
            capability = root.find('./capability')
            domain =  str(hex(int(capability.find('domain').text))).replace('0x', '')
            bus = str(hex(int(capability.find('bus').text))).replace('0x', '')
            slot =  str(hex(int(capability.find('slot').text))).replace('0x', '')
            function =  str(hex(int(capability.find('function').text))).replace('0x', '')
            try:
                driver = root.find('./driver/name').text
            except AttributeError:
                driver = ""
            pcidevicesList.append({
                "iommuGroup": int(iommuGroup), 
                "path": path,
                "productName": productName, 
                "productid": productid,
                "vendorName": vendorName, 
                "vendorid": vendorid, 
                "driver": driver, 
                "domain": domain, 
                "bus": bus, 
                "slot": slot, 
                "function": function,
                "label": f"{path} {productName}"
            })
        except AttributeError:
            pass
    # sort by path
    pcidevicesList = sorted(pcidevicesList, key=lambda k: k['path'])
    return pcidevicesList


class DomainPcie():
    def __init__(self, domuuid):
        self.domain = conn.lookupByUUIDString(domuuid)
        self.vmXml = self.domain.XMLDesc()

    @property
    def get(self):
        tree = ET.fromstring(self.vmXml)
        pcidevices = []
        hostdevs = tree.findall('./devices/hostdev')
        for hostdev in hostdevs:
            foundSystemPciDevice = False
            hostdevtype = hostdev.get('type')
            if hostdevtype == 'pci':
                xml = ET.tostring(hostdev).decode('utf-8')
                source_address = hostdev.find('source/address')
                domain = str(hex(int(source_address.get('domain'), 0))).replace('0x', '')
                bus = str(hex(int(source_address.get('bus'), 0))).replace('0x', '')
                slot = str(hex(int(source_address.get('slot'), 0))).replace('0x', '')
                function = str(hex(int(source_address.get('function'), 0))).replace('0x', '')
                romelem = hostdev.find('rom')
                romfile = ""
                customRomFile = False
                if romelem != None:
                    romfile = romelem.get('file')
                    customRomFile = True

                for i in HostPcieDevices():
                    systempcidomain = str((i['domain']))
                    systempcibus = str((i['bus']))
                    systempcislot = str((i['slot']))
                    systempcifunction = str((i['function']))
                    deviceProductName = i['productName']
                    deviceVendorName = i['vendorName']
                    devicepath = i['path']
                    if systempcidomain == domain and systempcibus == bus and systempcislot == slot and systempcifunction == function:
                        foundSystemPciDevice = True
                        break

                if not foundSystemPciDevice:
                    devicepath = "Unkonwn"
                    deviceProductName = "Unkown"
                    deviceVendorName = "Unknown"
                pcidevices.append({
                    "xml": xml,
                    "devicepath": devicepath,
                    "domain": domain,
                    "bus": bus,
                    "slot": slot,
                    "function": function,
                    "productName": deviceProductName,
                    "vendorName": deviceVendorName,
                    "customRomFile": customRomFile,
                    "romfile": romfile
                })

        return pcidevices

    def remove(self, domain, bus, slot, function):
        domainpciedevices = self.get
        for i in domainpciedevices:
            if i['domain'] == domain and i['bus'] == bus and i['slot'] == slot and i['function'] == function:
                pcidevicexml = i['xml']
                self.domain.detachDeviceFlags(pcidevicexml, libvirt.VIR_DOMAIN_AFFECT_CONFIG)

    def add(self, domain, bus, slot, function, romfile=None):
        print("inside add", romfile)
        if romfile == None:
            pcidevicexml = f"<hostdev mode='subsystem' type='pci' managed='yes'><source><address domain='{domain}' bus='{bus}' slot='{slot}' function='{function}'/></source></hostdev>"
        else:
            pcidevicexml = f"<hostdev mode='subsystem' type='pci' managed='yes'><source><address domain='{domain}' bus='{bus}' slot='{slot}' function='{function}'/></source>/><rom file='{romfile}'/></hostdev>"

        self.domain.attachDeviceFlags(pcidevicexml, libvirt.VIR_DOMAIN_AFFECT_CONFIG)

    def romfile(self, xml, romfile):
        origxml = xml
        tree = ET.fromstring(xml)
        rom_elem = tree.find('rom')
        if romfile == "":
            if rom_elem != None:
                rom_elem.attrib.pop('file')
        else:
            if rom_elem == None:
                rom_elem = ET.SubElement(tree, 'rom')
            rom_elem.set('file', romfile)

        xml = ET.tostring(tree).decode('utf-8')
        self.domain.detachDeviceFlags(origxml, libvirt.VIR_DOMAIN_AFFECT_CONFIG)
        # if xml fails to attach, revert to original xml
        try:
            self.domain.attachDeviceFlags(xml, libvirt.VIR_DOMAIN_AFFECT_CONFIG)
        except libvirt.libvirtError:
            self.domain.attachDeviceFlags(origxml, libvirt.VIR_DOMAIN_AFFECT_CONFIG)


class DomainUsb():
    def __init__(self, domuuid):
        self.domain = conn.lookupByUUIDString(domuuid)
        self.xml = self.domain.XMLDesc()

    @property
    def get(self):
        tree = ET.fromstring(self.xml)
        usbdevices = []
        hostdevs = tree.findall('./devices/hostdev')
        for hostdev in hostdevs:
            foundSystemUsbDevice = False
            hostdevtype = hostdev.get('type')
            if hostdevtype == 'usb':
                vendorid = hostdev.find('source/vendor').get("id")
                productid = hostdev.find('source/product').get("id")

                for i in SystemUsbDevicesList():
                    systemusbproductid = "0x"+i['productid']
                    systemusbvendorid = "0x"+i['vendorid']
                    systemusbname = i['name']

                    if int(systemusbvendorid, 0) == int(vendorid, 0) and int(systemusbproductid, 0) == int(productid, 0):
                        foundSystemUsbDevice = True
                        break
                if not foundSystemUsbDevice:
                    systemusbname = "Unknown"
                usbdevices.append(
                {
                    "name": systemusbname,
                    "vendorid": vendorid,
                    "productid": productid
                })
        return usbdevices

    def add(self, vendorid, productid, hotplug=False):
        xml = f"<hostdev mode='subsystem' type='usb' managed='no'><source><vendor id='{vendorid}'/><product id='{productid}'/></source></hostdev>"
        if hotplug:
            self.domain.attachDeviceFlags(
                xml, libvirt.VIR_DOMAIN_AFFECT_LIVE)
        else:
            self.domain.attachDeviceFlags(
                xml, libvirt.VIR_DOMAIN_AFFECT_CONFIG)

    def remove(self, vendorid, productid, hotplug=False):
        xml = f"<hostdev mode='subsystem' type='usb' managed='no'><source><vendor id='{vendorid}'/><product id='{productid}'/></source></hostdev>"
        if hotplug:
            self.domain.detachDeviceFlags(
                xml, libvirt.VIR_DOMAIN_AFFECT_LIVE)
        else:
            self.domain.detachDeviceFlags(
                xml, libvirt.VIR_DOMAIN_AFFECT_CONFIG)


class domainNetworkInterface():
    def __init__(self, dom_uuid):
        self.domain = conn.lookupByUUIDString(dom_uuid)
        self.domainxml = self.domain.XMLDesc()

    def get(self):
        networkinterfaces = []
        tree = ET.fromstring(self.domainxml)
        interfaces = tree.findall('./devices/interface')
        for number, interface in enumerate(interfaces):
            xml = ET.tostring(interface).decode()
            if interface.get('type') == "network":
                mac_addr = interface.find("mac").get('address')
                source_network = conn.networkLookupByName(interface.find("source").get('network')).name()
                model = interface.find('model').get("type")
                bootorderelem = interface.find('boot')
                if bootorderelem != None:
                    bootorder = bootorderelem.get("order")
                else:
                    bootorder = None
                networkinterfaces.append(
                {
                    'number': number, 
                    'xml': xml, 
                    'mac_addr': mac_addr, 
                    'source': source_network,
                    'model': model,
                    'bootorder': bootorder
                })
        return networkinterfaces

    def remove(self, index):
        for idx, interface in enumerate(self.get()):
            if idx == int(index):
                return interface['xml']


class create_vm():
    def __init__(self, name, machine_type, bios_type, mem_min, mem_min_unit, mem_max, mem_max_unit, disk=False, disk_size=None, disk_size_unit=None, disk_type=None, disk_bus=None, disk_location=None, iso=False, iso_location=None, network=False, network_source=None, network_model=None, ovmf_name=None):
        self.name = name
        self.machine_type = machine_type
        self.bios_type = bios_type
        self.min_mem_unit = mem_min_unit
        self.max_mem_unit = mem_max_unit
        self.mem_min = storage_manager.convertSizeUnit(size=int(mem_min), from_unit=mem_min_unit, to_unit="KB", mode='int')
        self.mem_max =storage_manager.convertSizeUnit(size=int(mem_max), from_unit=mem_max_unit, to_unit="KB", mode='int')
        self.disk = disk
        self.disk_size = disk_size
        self.disk_size_unit = disk_size_unit
        self.disk_type = disk_type
        self.disk_bus = disk_bus
        self.disk_location = disk_location
        self.iso = iso
        self.iso_location = iso_location
        self.network = network
        self.network_source = network_source
        self.network_model = network_model
        if ovmf_name:
            self.ovmf_path = settings_ovmfpaths().get(ovmf_name)
            self.ovmf_string = f"<loader readonly='yes' type='pflash'>{self.ovmf_path}</loader>"
        self.qemu_path = settings().get("qemu path")
        self.networkstring = ""
        if self.network:
            self.networkstring = f"<interface type='network'><source network='{conn.networkLookupByUUIDString(self.network_source).name()}'/><model type='{self.network_model}'/></interface>"
        
        self.createisoxml = ""
        if self.iso:
            self.createisoxml = f"""<disk type='file' device='cdrom'>
                            <driver name='qemu' type='raw'/>
                            <source file='{iso_location}'/>
                            <target dev='sda' bus='sata'/>
                            <boot order='2'/>
                            "<readonly/>
                            </disk>"""
        self.creatediskxml = ""
        if self.disk:
            disk_size = storage_manager.convertsize.convertSizeUnit(size=int(disk_size), from_unit=self.disk_size_unit, to_unit="B", mode='int')
            disk_volume_name = f"{self.name}-0.{self.disk_type}"
            disk_location = os.path.join(self.disk_location, disk_volume_name)
            try:
                subprocess.check_output(["qemu-img", "create", "-f", self.disk_type, disk_location, f"{disk_size}B"])
            except subprocess.CalledProcessError as e:
                raise Exception(f"Error: Creating disk failed with error: {e}")

            self.creatediskxml = f"""<disk type='file' device='disk'>
                            <driver name='qemu' type='{self.disk_type}'/>
                            <source file='{disk_location}'/>
                            <target dev='{"vda" if self.disk_bus == "virtio" else "sdb"}' bus='{self.disk_bus}'/>
                            <boot order='1'/>
                            </disk>"""

    def windows(self, version):
        self.tpmxml = f"""<tpm model='tpm-tis'>
        <backend type='emulator' version='2.0'/>
        </tpm>"""
        self.xml = f"""<domain type='kvm'>
        <name>{self.name}</name>
        <metadata>
            <libosinfo:libosinfo xmlns:libosinfo="http://libosinfo.org/xmlns/libvirt/domain/1.0">
            <libosinfo:os id="http://microsoft.com/win/{version}"/>
            </libosinfo:libosinfo>
        </metadata>
        <memory unit='KiB'>{self.mem_max}</memory>
        <currentMemory unit='KiB'>{self.mem_min}</currentMemory>
        <vcpu>2</vcpu>
        <os>
            <type arch='x86_64' machine='{self.machine_type}'>hvm</type>
            {self.ovmf_string if self.bios_type == "ovmf" else ""}
        </os>
        <features>
            <acpi/>
            <apic/>
            <hyperv mode='custom'>
            <relaxed state='on'/>
            <vapic state='on'/>
            <spinlocks state='on' retries='8191'/>
            </hyperv>
            <vmport state='off'/>
        </features>
        <cpu mode='host-model' check='partial'/>
        <devices>
            <emulator>{self.qemu_path}</emulator>
            {self.networkstring}
            {self.createisoxml}
            {self.creatediskxml}
            <graphics type='vnc' port='-1'/>
            <video>
            <model type='virtio'/>
            </video>
            <input type='tablet' bus='usb'/>
            # if version == "11", then add xml device
            {self.tpmxml if version == "11" else ""}
        </devices>
        </domain>"""
        return self.xml

    def macos(self, version):
        self.xml = f"""<domain type='kvm' xmlns:qemu='http://libvirt.org/schemas/domain/qemu/1.0'>
        <name>{self.name}</name>
        <memory unit='KiB'>{self.mem_max}</memory>
        <currentMemory unit='KiB'>{self.mem_min}</currentMemory>
        <vcpu>2</vcpu>
        <os>
            <type arch='x86_64' machine='{self.machine_type}'>hvm</type>
            {self.ovmf_string if self.bios_type == "ovmf" else ""}
        </os>
        <features>
            <acpi/>
            <apic/>
        </features>
        <cpu mode='host-passthrough' check='none' migratable='on'>
            <topology sockets='1' dies='1' cores='2' threads='1'/>
            <cache mode='passthrough'/>
        </cpu>
        <clock offset='localtime'>
            <timer name='rtc' tickpolicy='catchup'/>
            <timer name='pit' tickpolicy='delay'/>
            <timer name='hpet' present='no'/>
            <timer name='tsc' present='yes' mode='native'/>
        </clock>
        <devices>
            <emulator>{self.qemu_path}</emulator>
            {self.networkstring}
            {self.createisoxml}
            {self.creatediskxml}
            <serial type='pty'>
                <target type='isa-serial' port='0'>
                    <model name='isa-serial'/>
                </target>
            </serial>
            <console type='pty'>
                <target type='serial' port='0'/>
            </console>
            <channel type='unix'>
                <target type='virtio' name='org.qemu.guest_agent.0'/>
            </channel>
            <graphics type='vnc' port='-1'/>
            <video>
                <model type='vga' vram='65536' heads='1' primary='yes'/>
            </video>
            <input type='tablet' bus='usb'/>
            <memballoon model='none'/>
        </devices>
        <qemu:commandline>
        <qemu:arg value='-global'/>
        <qemu:arg value='ICH9-LPC.acpi-pci-hotplug-with-bridge-support=off'/>
        <qemu:arg value='-device'/>
        <qemu:arg value='isa-applesmc,osk=ourhardworkbythesewordsguardedpleasedontsteal(c)AppleComputerInc'/>
        <qemu:arg value='-cpu'/>
        {"<qemu:arg value='Cascadelake-Server,vendor=GenuineIntel'/>" if float(version) >= 13 else "<qemu:arg value='host,vendor=GenuineIntel'/>"}
    </qemu:commandline>
        </domain>"""
        return self.xml

    def linux(self):
        self.xml = f"""<domain type='kvm'>
        <name>{self.name}</name>
        <metadata>
            <libosinfo:libosinfo xmlns:libosinfo="http://libosinfo.org/xmlns/libvirt/domain/1.0">
            </libosinfo:libosinfo>
        </metadata>
        <memory unit='KiB'>{self.mem_max}</memory>
        <currentMemory unit='KiB'>{self.mem_min}</currentMemory>
        <vcpu>2</vcpu>
        <os>
            <type arch='x86_64' machine='{self.machine_type}'>hvm</type>
            {self.ovmf_string if self.bios_type == "ovmf" else ""}
        </os>
        <features>
            <acpi/>
            <apic/>
            <hyperv mode='custom'>
            <relaxed state='on'/>
            <vapic state='on'/>
            <spinlocks state='on' retries='8191'/>
            </hyperv>
            <vmport state='off'/>
        </features>
        <cpu mode='host-model' check='partial'/>
        <devices>
            <emulator>{self.qemu_path}</emulator>
            {self.networkstring}
            {self.createisoxml}
            {self.creatediskxml}
            <graphics type='vnc' port='-1'/>
            <video>
            <model type='virtio'/>
            </video>
            <input type='tablet' bus='usb'/>
            <channel type='unix'>
                <target type='virtio' name='org.qemu.guest_agent.0'/>
            </channel>
            <rng model='virtio'>
                <backend model='random'>/dev/urandom</backend>
            </rng>
        </devices>
        </domain>"""
        return self.xml
    def create(self):
        conn.defineXML(self.xml)

class DomainGraphics:
    def __init__(self, domuuid):
        self.domain = conn.lookupByUUIDString(domuuid)
        self.xml = ET.fromstring(self.domain.XMLDesc(0))

    @property
    def get(self):
        graphicsDevices = []
        for index, i in enumerate(self.xml.findall("devices/graphics")):
            graphics_type = i.attrib["type"]
            graphicsDevices.append(
            {
                "index": index, 
                "type": graphics_type, 
            })
        return graphicsDevices

    def add(self, graphics_type):
        original_domain_xml = self.domain.XMLDesc(0)
        graphics_element = ET.Element("graphics")
        graphics_element.attrib["type"] = graphics_type
        self.xml.find("devices").append(graphics_element)
        newxml = ET.tostring(self.xml).decode("utf-8")
        self.domain.undefineFlags(4)
        try:
            self.domain = conn.defineXML(newxml)
        except libvirt.libvirtError as e:
            self.domain = conn.defineXML(original_domain_xml)
            raise e

    def remove(self, index):
        original_domain_xml = self.domain.XMLDesc(0)
        graphics_element = self.xml.find(f"devices/graphics/[{index+1}]")

        # remove all elements from graphics element
        for i in graphics_element:
            graphics_element.remove(i)

        # remove all attributes from graphics element
        graphics_element.attrib.clear()

        # remove graphics element
        self.xml.find("devices").remove(graphics_element)

        # remove graphics element
        newxml = ET.tostring(self.xml).decode("utf-8")
        
        # define new xml
        self.domain.undefineFlags(4)
        try:
            self.domain = conn.defineXML(newxml)
        except libvirt.libvirtError as e:
            self.domain = conn.defineXML(original_domain_xml)
            raise e


class DomainVideo:
    def __init__(self, domuuid):
        self.domain = conn.lookupByUUIDString(domuuid)
        self.xml = ET.fromstring(self.domain.XMLDesc(0))
    
    @property
    def get(self):
        videoDevices = []
        for index, i in enumerate(self.xml.findall("devices/video")):
            xml = ET.tostring(i).decode("utf-8")
            model_type = i.find("model").attrib["type"]
            videoDevices.append(
            {
                "index": index, 
                "type": model_type, 
                "xml": xml
            })
        return videoDevices
    
    def add(self, model_type):
        original_domain_xml = self.domain.XMLDesc(0)
        video_element = ET.Element("video")
        video_model_element = ET.Element("model")
        video_model_element.attrib["type"] = model_type
        video_element.append(video_model_element)
        self.xml.find("devices").append(video_element)
        newxml = ET.tostring(self.xml).decode("utf-8")
        self.domain.undefineFlags(4)
        try:
            self.domain = conn.defineXML(newxml)
        except libvirt.libvirtError as e:
            self.domain = conn.defineXML(original_domain_xml)
            raise e
    
    def remove(self, index):
        original_domain_xml = self.domain.XMLDesc(0)
        video_element = self.xml.find(f"devices/video/[{index+1}]")

        # remove all elements from video element
        for i in video_element:
            video_element.remove(i)

        # remove all attributes from video element
        video_element.attrib.clear()

        # remove video element
        self.xml.find("devices").remove(video_element)

        # remove video element
        newxml = ET.tostring(self.xml).decode("utf-8")
        
        # define new xml
        self.domain.undefineFlags(4)
        try:
            self.domain = conn.defineXML(newxml)
        except libvirt.libvirtError as e:
            self.domain = conn.defineXML(original_domain_xml)
            raise e
        
class DomainSound:
    def __init__(self, domuuid):
        self.domain = conn.lookupByUUIDString(domuuid)
        self.xml = ET.fromstring(self.domain.XMLDesc(0))
    
    @property
    def get(self):
        soundDevices = []
        for index, i in enumerate(self.xml.findall("devices/sound")):
            xml = ET.tostring(i).decode("utf-8")
            model = i.get("model")
            soundDevices.append(
            {
                "index": index, 
                "model": model, 
                "xml": xml
            })
        return soundDevices
    
    def add(self, model):
        original_domain_xml = self.domain.XMLDesc(0)
        sound_element = ET.Element("sound")
        sound_element.attrib["model"] = model
        self.xml.find("devices").append(sound_element)
        newxml = ET.tostring(self.xml).decode("utf-8")
        self.domain.undefineFlags(4)
        try:
            self.domain = conn.defineXML(newxml)
        except libvirt.libvirtError as e:
            self.domain = conn.defineXML(original_domain_xml)
            raise e
    
    def remove(self, index):
        original_domain_xml = self.domain.XMLDesc(0)
        sound_element = self.xml.find(f"devices/sound/[{index+1}]")

        # remove all elements from sound element
        for i in sound_element:
            sound_element.remove(i)

        # remove all attributes from sound element
        sound_element.attrib.clear()

        # remove sound element
        self.xml.find("devices").remove(sound_element)

        # remove sound element
        newxml = ET.tostring(self.xml).decode("utf-8")
        
        # define new xml
        self.domain.undefineFlags(4)
        try:
            self.domain = conn.defineXML(newxml)
        except libvirt.libvirtError as e:
            self.domain = conn.defineXML(original_domain_xml)
            raise e

def getGuestMachineTypes():
    capabilities = conn.getCapabilities()
    root = ET.fromstring(capabilities)
    machine_types = []
    for arch in root.findall('.//arch[@name="x86_64"]'):
        for machine in arch.findall('machine'):
            machine_types.append(machine.text)
    # filter to only pc-i440fx and pc-q35
    machine_types = [x for x in machine_types if x.startswith('pc-i440fx') or x.startswith('pc-q35')]
    machine_types.sort()
    return machine_types

class settings:
    def __init__(self):
        self.db = sqlite3.connect('database.db')
        self.db_c = self.db.cursor()

    def getAll(self):
        self.db_c.execute('''
        SELECT * FROM settings
        ''')
        rows = self.db_c.fetchall()

        settingsData = []

        for row in rows:
            name = row[1]
            value = row[2]
            settingsData.append(
            {
                "name": name,
                "value": value
            })

        return settingsData
    
    # get value of setting by setting name
    def get(self, name):
        self.db_c.execute('''
        SELECT * FROM settings WHERE name = ?
        ''', (name,))
        row = self.db_c.fetchone()

        return row[2]
    
    def set(self, name, value):
        self.db_c.execute('''
        UPDATE settings SET value = ? WHERE name = ?
        ''', (value, name))
        self.db.commit()

class settings_ovmfpaths:
    def __init__(self):
        self.db = sqlite3.connect('database.db')
        self.db_c = self.db.cursor()

    def getAll(self):
        self.db_c.execute('''
        SELECT * FROM settings_ovmfpaths
        ''')
        rows = self.db_c.fetchall()

        settingsData = []

        for row in rows:
            name = row[1]
            path = row[2]
            settingsData.append(
            {
                "name": name,
                "path": path
            })

        return settingsData

    # get path of ovmf by name
    def get(self, name):
        self.db_c.execute('''
        SELECT * FROM settings_ovmfpaths WHERE name = ?
        ''', (name,))
        row = self.db_c.fetchone()

        return row[2]
    
    def delete(self, name):
        self.db_c.execute('''
        DELETE FROM settings_ovmfpaths WHERE name = ?
        ''', (name,))
        self.db.commit()

    def add(self, name, path):
        self.db_c.execute('''
        INSERT INTO settings_ovmfpaths (name, path) VALUES (?, ?)
        ''', (name, path))
        self.db.commit()

    def set(self, name, path):
        self.db_c.execute('''
        UPDATE settings_ovmfpaths SET path = ? WHERE name = ?
        ''', (path, name))
        self.db.commit()

@app.get("/")
def index():
    return FileResponse("templates/index.html")

### Websockets ###
@app.websocket("/notifications")
async def websocket_endpoint(websocket: WebSocket, token: str):
    await websocket.accept()
    notifications_list = None
    try:
        if check_auth_token(token):
            notifications_list = notification_manager.get_notifications()
            await websocket.send_json({"type": "notifications_init", "data": notifications_list})
        while True:
            if check_auth_token(token):
                new_notifications_list = notification_manager.get_notifications()
                if notifications_list != new_notifications_list:
                    new_notifications = [x for x in new_notifications_list if x not in notifications_list]
                    notifications_list = new_notifications_list
                    await websocket.send_json({"type": "notifications", "data": new_notifications})
                await asyncio.sleep(1)
            else:
                await websocket.send_json({"type": "auth_error"})
                await websocket.close()
                break
    except WebSocketDisconnect:
        pass

@app.websocket("/dashboard")
async def websocket_endpoint(websocket: WebSocket, token: str):
    await websocket.accept()
    try:
        if check_auth_token(token):
            sysInfo = ET.fromstring(conn.getSysinfo(0))
            cpu_name = sysInfo.find("processor/entry[@name='version']").text
            mem_total = storage_manager.convertSizeUnit(psutil.virtual_memory().total, from_unit="B", to_unit="GB", round_state=True, round_to=2)
            os_name = distro.name(pretty=True)
            uptime = humanize.precisedelta(datetime.now() - datetime.fromtimestamp(psutil.boot_time()), minimum_unit="minutes", format="%0.0f")
            await websocket.send_json({"type": "dashboard_init", "data": {"cpu_name": cpu_name, "mem_total": mem_total, "os_name": os_name, "uptime": uptime}})
        while True:
            if check_auth_token(token):
                cpu_percent = int(psutil.cpu_percent())
                cpu_thread_data = psutil.cpu_percent(interval=1, percpu=True)
                mem_used = storage_manager.convertSizeUnit(psutil.virtual_memory().used, from_unit="B", to_unit="GB", round_state=True, round_to=2)
                message = {"cpu_percent": cpu_percent, "cpu_thread_data": cpu_thread_data, "mem_used": mem_used}
                await websocket.send_json({"type": "dashboard", "data": message})
                await asyncio.sleep(1)
            else:
                await websocket.send_json({"type": "auth_error"})
                await websocket.close()
                break
    except WebSocketDisconnect:
        pass

@app.websocket("/vmdata")
async def websocket_endpoint(websocket: WebSocket, token: str):
    await websocket.accept()
    vm_list = None
    try:
        while True:
            if check_auth_token(token):
                # only send new data if the vm list has changed
                new_vm_list = getvmresults()
                if vm_list == None or vm_list != new_vm_list:
                    vm_list = new_vm_list
                    await websocket.send_json({"type": "vmdata", "data": vm_list})
                await asyncio.sleep(1)
            else:
                await websocket.send_json({"type": "auth_error"})
                await websocket.close()
                break
    except WebSocketDisconnect:
        pass

@app.websocket("/downloadiso")
async def websocket_endpoint(websocket: WebSocket, token: str):
    await websocket.accept()
    if check_auth_token(token):
        data = await websocket.receive_json()
        url = data["url"]
        filename = data["fileName"]
        directory = data["directory"]
        filepath = os.path.join(directory, filename)

        # use websocket events to send progress and errors
        # downloadISOError: on error
        # downloadISOProgress: on progress
        # downloadISOComplete: on complete

        if (os.path.isfile(filepath)):
            await websocket.send_json({"event": "downloadISOError", "message": f"{filename} already exists in {directory}"})
            return
        
        try:
            response = requests.get(url, stream=True)
            if response.status_code != 200:
                await websocket.send_json({"event": "downloadISOError", "message": f"Response code: {response.status_code}"})
                return
            try:
                total_size = int(response.headers.get('content-length'))
            except TypeError as e:
                websocket.send_json({"event": "downloadISOError", "message": f"Content-Length not found in response headers. Error: {e}"})
                return
            chunk_size = 1000

            with open(filepath, 'wb') as f:
                percentage = 0
                for index, data in enumerate(response.iter_content(chunk_size)):
                    prev_percentage = percentage
                    percentage = round(index * chunk_size / total_size * 100)
                    if prev_percentage != percentage:
                        await websocket.send_json({"event": "downloadISOProgress", "percentage": percentage})
                        if percentage == 100:
                            print("download complete")
                            await websocket.send_json({"event": "downloadISOComplete", "message": ["ISO Download Complete", f"ISO File: {filename}", f"Directory: {directory}"]})
                    f.write(data)
                    await asyncio.sleep(0) # allow the websocket to send the message before continuing
        except Exception as e:
            await websocket.send_json({"event": "downloadISOError", "message": f"Error: {e}"})
    else:
        await websocket.send_json({"event": "auth_error"})
        await websocket.close()

# changes the size reported to TTY-aware applications like vim
def set_winsize(fd, row, col, xpix=0, ypix=0):
    winsize = struct.pack("HHHH", row, col, xpix, ypix)
    fcntl.ioctl(fd, termios.TIOCSWINSZ, winsize)

async def read_and_forward_pty_output(websocket: WebSocket):
    global fd
    max_read_bytes = 1024 * 20
    while True:
        await asyncio.sleep(0.01)
        if fd:
            timeout_sec = 0
            (data_ready, _, _) = select.select([fd], [], [], timeout_sec)
            if data_ready:
                output = os.read(fd, max_read_bytes).decode()
                await websocket.send_json({"type": "pty_output", "output": output})
        else:
            return

def kill_child_process():
    global child_pid
    global fd
    os.kill(child_pid, signal.SIGKILL)
    fd = None
    child_pid = None
    print("pty closed")

@app.websocket("/terminal")
async def pty_socket(websocket: WebSocket, token: str):
    global fd
    global child_pid

    await websocket.accept()

    if child_pid:
        # already started child process, don't start another
        # write a new line so that when a client refresh the shell prompt is printed
        os.write(fd, "\n".encode())
        # return

    # create child process attached to a pty we can read from and write to
    (child_pid, fd) = os.forkpty()

    if child_pid == 0:
        # this is the child process fork.
        # anything printed here will show up in the pty, including the output
        # of this subprocess
        # run bash in /root
        subprocess.run(["/bin/bash"], cwd="/root", env={"TERM": "xterm"})


    else:
        try:
            # this is the parent process fork.
            asyncio.create_task(read_and_forward_pty_output(websocket))
            while True:
                message = await websocket.receive_json()
                if check_auth_token(token):
                    if message['type'] == 'input':
                        os.write(fd, message["input"].encode())
                    elif message['type'] == 'resize':
                        set_winsize(fd, message["dims"]['rows'], message["dims"]['cols'])
                else:
                    await websocket.send_json({"type": "auth_error"})
                    await websocket.close()
                    kill_child_process()
                    break
        except WebSocketDisconnect:
            print("Websocket connection to terminal is closed")
            # close the pty
            kill_child_process()
            

@app.get('/api/no-auth/hostname')
async def get_hostname(request: Request):
    return JSONResponse(content={"hostname": conn.getHostname()})

@app.get('/api/no-auth/system-status')
async def get_system_status(request: Request):
    global system_status
    return system_status

@app.post('/api/login')
async def login(request: Request):
    data = await request.json()
    username = data['username']
    password = data['password']

    if not username:
        return HTTPException(status_code=400, detail="Username is required")
    if not password:
        return HTTPException(status_code=400, detail="Password is required")
    
    if pam.authenticate(username, password):
        expire_time_seconds = int(settings().get("login token expire"))
        expires_delta = timedelta(seconds=expire_time_seconds)
        expire = datetime.utcnow() + expires_delta
        token = jwt.encode({"username": username, "exp": expire}, SECRET_KEY, algorithm=ALGORITHM, )
        print("auth success")
        return JSONResponse(content={"access_token": token})
    else:
        return HTTPException(status_code=401, detail="Invalid username or password")


### API/VM-MANAGER ###
@app.get('/api/vm-manager/{action}')
async def get_vm_manager(request: Request, action: str, username: str = Depends(check_auth)):
    if action == "running":
        domainList = []
        for domain in conn.listAllDomains():
            if domain.isActive():
                domainList.append({
                    "name": domain.name(),
                    "uuid": domain.UUIDString(),
                })
        return domainList
    elif action == "all":
        return getvmresults()
    else:
        return JSONResponse(content={"error": "Invalid action"})

@app.post('/api/vm-manager/{action}')
async def post_vm_manager(request: Request, action: str, username: str = Depends(check_auth)):
    if action == "create":
        form_data = await request.form()
        name = form_data.get('name')
        os = form_data.get('os')
        machine_type = form_data.get('machine_type')
        bios_type = form_data.get('bios_type')
        ovmf_name = None
        if bios_type == "ovmf":
            ovmf_name = form_data.get('ovmf_name')
            print("ovmf_name: " + ovmf_name)
        min_mem = form_data.get('memory_min')
        mim_mem_unit = form_data.get('memory_min_unit')
        max_mem = form_data.get('memory_max')
        max_mem_unit = form_data.get('memory_max_unit')
        disk = True
        disk_size = form_data.get('disk_size')
        disk_size_unit = form_data.get('disk_size_unit')
        disk_type = form_data.get('disk_type')
        disk_bus = form_data.get('disk_bus')
        disk_location = form_data.get('disk_location')
        iso = True
        cdrom_location = form_data.get('cdrom_location')
        network = True
        network_source = form_data.get('network_source')
        network_model = form_data.get('network_model')

        print("name: " + name)
        print("os: " + os)
        print("machine_type: " + machine_type)
        print("bios_type: " + bios_type)
        print("min_mem: " + min_mem)
        print("mim_mem_unit: " + mim_mem_unit)
        print("max_mem: " + max_mem)
        print("max_mem_unit: " + max_mem_unit)
        print("disk: " + str(disk))
        print("disk_size: " + disk_size)
        print("disk_size_unit: " + disk_size_unit)
        print("disk_type: " + disk_type)
        print("disk_bus: " + disk_bus)
        print("disk_location: " + disk_location)
        print("iso: " + str(iso))
        print("cdrom_location: " + cdrom_location)
        print("network: " + str(network))
        print("network_source: " + network_source)
        print("network_model: " + network_model)

        try:
            vm = create_vm(name=name, machine_type=machine_type, bios_type=bios_type, mem_min=min_mem, mem_min_unit=mim_mem_unit, mem_max=max_mem, mem_max_unit=max_mem_unit, disk=disk,
                        disk_size=disk_size, disk_size_unit=disk_size_unit, disk_type=disk_type, disk_bus=disk_bus, disk_location=disk_location, iso=iso, iso_location=cdrom_location, network=network, network_source=network_source, network_model=network_model, ovmf_name=ovmf_name)
            if os == "Microsoft Windows 11":
                vm.windows(version="11")
            elif os == "Microsoft Windows 10":
                vm.windows(version="10")
            elif os == "Microsoft Windows 8.1":
                vm.windows(version="8.1")
            elif os == "Microsoft Windows 8":
                vm.windows(version="8")
            elif os == "Microsoft Windows 7":
                vm.windows(version="7")
            elif os == "macOS 10.15 Catalina":
                vm.macos(version="10.15")
            elif os == "macOS 11 Big Sur":
                print("macOS 11 Big Sur")
                print(vm.macos(version="11"))
            elif os == "macOS 12 Monterey":
                vm.macos(version="12")
            elif os == "macOS 13 Ventura":
                vm.macos(version="13")
            elif os == "Linux":
                print("Creating new linux vm")
                vm.linux()
            else:
                raise HTTPException(status_code=404, detail="OS not supported")
            vm.create()
            return
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

#### API/VM-MANAGER-ACTIONS ####
@app.get('/api/vm-manager/{vmuuid}/{action}')
async def get_vm_manager_actions(request: Request, vmuuid: str, action: str, username: str = Depends(check_auth)):
    domain = conn.lookupByUUIDString(vmuuid)
    domain_xml = domain.XMLDesc()
    if action == "xml":
        return { "xml": domain_xml }
    elif action == "disk-data":
        try:
            return storage(domain_uuid=vmuuid).get()
        except Exception as e:
            return {"error": f"{e}"}
    elif action == "logs":
        domain_name = domain.name()
        libvirt_domain_logs_path = settings().get("libvirt domain logs path")
        domain_log_path = os.path.join(libvirt_domain_logs_path, domain_name + ".log")
        if os.path.exists(domain_log_path):
            with open(domain_log_path, "r") as f:
                return { "log": f.read() }
        else:
            raise HTTPException(status_code=404, detail="Log file not found")
        
    elif action == "data":
        domain_xml = ET.fromstring(domain_xml)
        # get cpu model from xml
        cpu_model = domain_xml.find('cpu').get('mode')
        # get vcpus from xml
        vcpu = domain_xml.find('vcpu').text
        try:
            current_vcpu = domain_xml.find('vcpu').attrib['current']
        except KeyError:
            current_vcpu = vcpu
        
        topologyelem = domain_xml.find('cpu/topology')
        if topologyelem is None:
            custom_topology = False
            sockets = vcpu
            dies = 1
            cores = 1
            threads = 1
        else:
            sockets = topologyelem.attrib['sockets']
            dies = topologyelem.attrib['dies']
            cores = topologyelem.attrib['cores']
            threads = topologyelem.attrib['threads']
            custom_topology = True
            
        
        # get machine type
        machine_type = domain_xml.find('os/type').attrib['machine']
        # get bios type
        os_loader_elem = domain_xml.find('os/loader')
        bios_type = "BIOS"
        if os_loader_elem != None:
            bios_type = os_loader_elem.text

        # get autostart boolean
        autostart = False
        if domain.autostart() == 1:
            autostart = True
            
        # get memory
        meminfo = vmmemory(uuid=vmuuid).current()
        minmem = storage_manager.convertSizeUnit(meminfo[0], from_unit="KB", mode="tuple")
        maxmem = storage_manager.convertSizeUnit(meminfo[1], from_unit="KB", mode="tuple")
        minmem_size = minmem[0]
        minmem_unit = minmem[1]
        maxmem_size = maxmem[0]
        maxmem_unit = maxmem[1]

        # get disk
        diskinfo = storage(domain_uuid=vmuuid).get()
        networks = domainNetworkInterface(dom_uuid=vmuuid).get()

        # graphics tab            
        graphicsdevices = DomainGraphics(domuuid=vmuuid).get
        videodevices = DomainVideo(domuuid=vmuuid).get

        # sound tab
        sounddevices = DomainSound(domuuid=vmuuid).get

        # passthrough devices
        usbdevices = DomainUsb(domuuid=vmuuid).get
        pcidevices = DomainPcie(domuuid=vmuuid).get

        data = {
            "name": domain.name(),
            "autostart": autostart,
            "current_vcpu": current_vcpu,
            "cpu_model": cpu_model,
            "vcpu": vcpu,
            "current_vcpu": current_vcpu,
            "custom_topology": custom_topology,
            "topology_sockets": sockets,
            "topology_dies": dies,
            "topology_cores": cores,
            "topology_threads": threads,
            "uuid": domain.UUIDString(),
            "state": domain.state()[0],
            "machine": machine_type,
            "bios": bios_type,
            "memory_max": maxmem_size,
            "memory_max_unit": maxmem_unit,
            "memory_min": minmem_size,
            "memory_min_unit": minmem_unit,
            "disks": diskinfo,
            "networks": networks,
            "sounddevices": sounddevices,
            "usbdevices": usbdevices,
            "pcidevices": pcidevices,
            "graphicsdevices": graphicsdevices,
            "videodevices": videodevices
        }
        return data
    else:
        raise HTTPException(status_code=404, detail="Action not found")

@app.post('/api/vm-manager/{vmuuid}/{action}')
async def post_vm_manager_actions(request: Request, vmuuid: str, action: str, username: str = Depends(check_auth)):
    domain = conn.lookupByUUIDString(vmuuid)
    if action == "start":
        try:
            if domain.state()[0] == libvirt.VIR_DOMAIN_SHUTOFF:
                domain.create()
                return
            elif domain.state()[0] == libvirt.VIR_DOMAIN_PMSUSPENDED:
                domain.pMWakeup()
                return
            else:
                raise HTTPException(status_code=400, detail="Domain is in an invalid state")
        except libvirt.libvirtError as e:
            raise HTTPException(status_code=500, detail=str(e))

    elif action == "stop":
        try:
            domain.shutdown()
            return
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    elif action == "forcestop":
        try:
            domain.destroy()
            return
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    elif action == "remove":
        try:
            # flag 4 = also remove any nvram file
            domain.undefineFlags(4)
            return
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    elif action == "autostart":
        data = await request.json()
        value = data['autostart']
        try:
            if value == True:
                domain.setAutostart(1)
            else:
                domain.setAutostart(0)
            return
        except libvirt.libvirtError as e:
            raise HTTPException(status_code=500, detail=str(e))

    elif action.startswith("edit"):
        data = await request.json()
        action = action.replace("edit-", "")
        if action == "xml":
            xml = data['xml']
            origxml = domain.XMLDesc(0)
            try:
                domain.undefineFlags(4)
            except libvirt.libvirtError as e:
                raise HTTPException(status_code=500, detail=str(e))
            try:
                domain = conn.defineXML(xml)
                return
            except libvirt.libvirtError as e:
                try:
                    domain = conn.defineXML(origxml)
                    raise HTTPException(status_code=500, detail=str(e))
                except libvirt.libvirtError as e2:
                    raise HTTPException(status_code=500, detail=str(e2))

        elif action.startswith("general"):
            action = action.replace("general-", "")
            value = data['value']
            if action == "name":
                xml = ET.fromstring(domain.XMLDesc(0))
                xml.find('name').text = value
                xml = ET.tostring(xml).decode()
                try:
                    domain.undefineFlags(4)
                    domain = conn.defineXML(xml)
                    return
                except libvirt.libvirtError as e:
                    raise HTTPException(status_code=500, detail=str(e))
            elif action == "autostart":
                if value == True:
                    value = 1
                else:
                    value = 0
                try:
                    domain.setAutostart(value)
                    return
                except libvirt.libvirtError as e:
                    raise HTTPException(status_code=500, detail=str(e))

        # edit-cpu
        elif action == "cpu":
            model = data['cpu_model']
            vcpu = str(data['vcpu'])
            current_vcpu = str(data['current_vcpu'])
            custom_topology = data['custom_topology']
            sockets = str(data['topology_sockets'])
            dies = str(data['topology_dies'])
            cores = str(data['topology_cores'])
            threads = str(data['topology_threads'])
            vm_xml = ET.fromstring(domain.XMLDesc(0))
            # set cpu model
            cpu_elem  = vm_xml.find('cpu')
            cpu_elem.set('mode', model)
            # remove migratable from cpu element
            if cpu_elem.attrib.get('migratable') != None:
                cpu_elem.attrib.pop('migratable')
            

            if custom_topology:
                # new dict for topology
                topologyelem = vm_xml.find('cpu/topology')
                if topologyelem != None:
                    topologyelem.set('sockets', sockets)
                    topologyelem.set('dies', dies)
                    topologyelem.set('cores', cores)
                    topologyelem.set('threads', threads)
                else:
                    topologyelem = ET.Element('topology')
                    topologyelem.set('sockets', sockets)
                    topologyelem.set('dies', dies)
                    topologyelem.set('cores', cores)
                    topologyelem.set('threads', threads)
                    vm_xml.find('cpu').append(topologyelem)
            
            vm_xml.find('vcpu').text = vcpu
            if current_vcpu != vcpu:
                vm_xml.find('vcpu').attrib['current'] = current_vcpu 
            vm_xml = ET.tostring(vm_xml).decode()
            try:
                domain.undefineFlags(4)
                domain = conn.defineXML(vm_xml)
                return
            except libvirt.libvirtError as e:
                raise HTTPException(status_code=500, detail=str(e))


        # edit-memory
        elif action == "memory":
            memory_min = int(data['memory_min'])
            memory_min_unit = data['memory_min_unit']
            memory_max = int(data['memory_max'])
            memory_max_unit = data['memory_max_unit']
            if memory_min > memory_max:
                raise HTTPException(status_code=400, detail="Minimum memory cannot be greater than maximum memory")
            else:
                vmmemory(uuid=vmuuid).edit(memory_min, memory_min_unit, memory_max, memory_max_unit)
                return

        # edit-network-action
        elif action.startswith("network"):
            action = action.replace("network-", "")
            if action == "add":
                source_network = data['sourceNetwork']
                model = data['networkModel']

                try:
                    source_network_name = conn.networkLookupByUUIDString(source_network).name()
                    xml = f"<interface type='network'><source network='{source_network_name}'/><model type='{model}'/></interface>"
                    domain.attachDeviceFlags(
                        xml, libvirt.VIR_DOMAIN_AFFECT_CONFIG)
                    return
                except libvirt.libvirtError as e:
                    raise HTTPException(status_code=500, detail=str(e))

            elif action == "delete":
                index = data['number']
                networkxml = domainNetworkInterface(dom_uuid=vmuuid).remove(index)
                try:
                    domain.detachDeviceFlags(networkxml, libvirt.VIR_DOMAIN_AFFECT_CONFIG)
                    return
                except libvirt.libvirtError as e:
                    raise HTTPException(status_code=500, detail=str(e))
            else:
                raise HTTPException(status_code=404, detail="Action not found")
        
        # edit-disk-action
        elif action.startswith("disk"):
            action = action.replace("disk-", "")
            if action != "add":
                disknumber = data['number']
                xml_orig = storage(domain_uuid=vmuuid).getxml(disknumber)
                xml = ET.fromstring(xml_orig)

            if action == "add":
                formDeviceType = data['deviceType']
                if formDeviceType == "cdrom" or formDeviceType == "existingvdisk":
                    formDeviceType = "disk" if formDeviceType == "existingvdisk" else "cdrom"
                    cdrompath = data['volumePath']
                    cdrombus = data['diskBus']
                    try:
                        storage(domain_uuid=vmuuid).add_xml(
                            disktype="file",
                            targetbus=cdrombus,
                            devicetype=formDeviceType,
                            drivertype="raw",
                            sourcefile=cdrompath
                        )
                        return
                    except libvirt.libvirtError as e:
                        raise HTTPException(status_code=500, detail=str(e))
                
                elif formDeviceType == "createvdisk":
                    directory = data['vdiskDirectory']
                    disksize = data['diskSize']
                    disksizeunit = data['diskSizeUnit']
                    diskType = data['diskDriverType']
                    diskBus = data['diskBus']
                    try:
                        storage(domain_uuid=vmuuid).createnew(
                            directory=directory,
                            disksize=disksize,
                            disksizeunit=disksizeunit,
                            disktype=diskType,
                            diskbus=diskBus
                        )
                        return
                    except libvirt.libvirtError as e:
                        raise HTTPException(status_code=500, detail=str(e))
                    
                elif formDeviceType == "block":
                    blockdev = data['sourceDevice']
                    diskBus = data['diskBus']
                    try:
                        storage(domain_uuid=vmuuid).add_xml(
                            disktype="block",
                            targetbus=diskBus,
                            devicetype="disk",
                            drivertype="raw",
                            sourcedev=blockdev
                        )
                        return
                    except libvirt.libvirtError as e:
                        raise HTTPException(status_code=500, detail=str(e))
                
                else:
                    raise HTTPException(status_code=400, detail="Invalid device type")

            elif action == "type":
                value = data['value']
                orig_value = xml.get('device')
                xml.set('device', value)
                if orig_value == "cdrom" and value == "disk":
                    xml.remove(xml.find('readonly'))
                xml = ET.tostring(xml).decode()
                try:
                    domain.detachDeviceFlags(xml_orig, libvirt.VIR_DOMAIN_AFFECT_CONFIG)
                    domain.attachDeviceFlags(xml, libvirt.VIR_DOMAIN_AFFECT_CONFIG)
                    return
                except libvirt.libvirtError as e:
                    raise HTTPException(status_code=500, detail=str(e))

            elif action == "driver-type":
                value = data['value']
                xml.find('driver').set('type', value)
                xml = ET.tostring(xml).decode()
                try:
                    domain.detachDeviceFlags(xml_orig, libvirt.VIR_DOMAIN_AFFECT_CONFIG)
                    domain.attachDeviceFlags(xml, libvirt.VIR_DOMAIN_AFFECT_CONFIG)
                    return
                except libvirt.libvirtError as e:
                    raise HTTPException(status_code=500, detail=str(e))

            elif action == "bus":
                value = data['value']
                xml.find('target').set('bus', value)
                xml.remove(xml.find('address'))
                xml = ET.tostring(xml).decode()
                try:
                    domain.detachDeviceFlags(xml_orig, libvirt.VIR_DOMAIN_AFFECT_CONFIG)
                    domain.attachDeviceFlags(xml, libvirt.VIR_DOMAIN_AFFECT_CONFIG)
                    return
                except libvirt.libvirtError as e:
                    raise HTTPException(status_code=500, detail=str(e))

            elif action == "source-file":
                value = data['value']
                xml.find('source').set('file', value)
                xml = ET.tostring(xml).decode()
                try:
                    domain.detachDeviceFlags(xml_orig, libvirt.VIR_DOMAIN_AFFECT_CONFIG)
                    domain.attachDeviceFlags(xml, libvirt.VIR_DOMAIN_AFFECT_CONFIG)
                    return
                except libvirt.libvirtError as e:
                    raise HTTPException(status_code=500, detail=str(e))
            
            elif action == "source-dev":
                value = data['value']
                xml.find('source').set('dev', value)
                xml = ET.tostring(xml).decode()
                try:
                    domain.detachDeviceFlags(xml_orig, libvirt.VIR_DOMAIN_AFFECT_CONFIG)
                    domain.attachDeviceFlags(xml, libvirt.VIR_DOMAIN_AFFECT_CONFIG)
                    return
                except libvirt.libvirtError as e:
                    raise HTTPException(status_code=500, detail=str(e))

            elif action == "bootorder":
                value = data['value']
                bootelem = xml.find('boot')
                if bootelem is None:
                    bootelem = ET.SubElement(xml, 'boot')
                bootelem.set('order', value)
                xml = ET.tostring(xml).decode()
                try:
                    domain.detachDeviceFlags(xml_orig, libvirt.VIR_DOMAIN_AFFECT_CONFIG)
                    domain.attachDeviceFlags(xml, libvirt.VIR_DOMAIN_AFFECT_CONFIG)
                    return
                except libvirt.libvirtError as e:
                    raise HTTPException(status_code=500, detail=str(e))

            elif action == "delete":
                try:
                    domain.detachDeviceFlags(xml_orig, libvirt.VIR_DOMAIN_AFFECT_CONFIG)
                    return
                except libvirt.libvirtError as e:
                    raise HTTPException(status_code=500, detail=str(e))
            else:
                raise HTTPException(status_code=404, detail="Action not found")

        # edit-usbhotplug-action
        elif action.startswith("usbhotplug"):
            action = action.replace("usbhotplug-", "")
            if action == "add":
                product_id = data['productid']
                vendor_id = data['vendorid']
                print("add usb hotplug", product_id, vendor_id)
                try:
                    xml = DomainUsb(vmuuid).add(vendorid=f"0x{vendor_id}", productid=f"0x{product_id}", hotplug=True)
                    return
                except Exception as e:
                    raise HTTPException(status_code=500, detail=str(e))
            elif action == "delete":
                product_id = data['productid']
                vendor_id = data['vendorid']
                print("delete usb hotplug", product_id, vendor_id)
                try:
                    xml = DomainUsb(vmuuid).remove(vendorid=f"0x{vendor_id}", productid=f"0x{product_id}", hotplug=True)
                    return
                except Exception as e:
                    raise HTTPException(status_code=500, detail=str(e))
            else:
                raise HTTPException(status_code=404, detail="Action not found")

        # edit-usb-action
        elif action.startswith("usb"):
            action = action.replace("usb-", "")
            if action == "add":
                print("add usb")
                product_id = data['productid']
                vendor_id = data['vendorid']
                try:
                    xml = DomainUsb(vmuuid).add(vendorid=f"0x{vendor_id}", productid=f"0x{product_id}")
                    return
                except Exception as e:
                    raise HTTPException(status_code=500, detail=str(e))
            elif action == "delete":
                product_id = data['productid']
                vendor_id = data['vendorid']
                try:
                    xml = DomainUsb(vmuuid).remove(vendorid=vendor_id, productid=product_id)
                    return
                except Exception as e:
                    raise HTTPException(status_code=500, detail=str(e))
            else:
                raise HTTPException(status_code=404, detail="Action not found")

        # edit-pcie-action
        elif action.startswith("pcie"):
            action = action.replace("pcie-", "")
            if action == "add":
                domain = "0x" + data['domain']
                bus = "0x" + data['bus']
                slot = "0x" + data['slot']
                function = "0x" + data['function']
                custom_rom_file = data['customRomFile']
                rom_file = data['romFile']
                try:
                    if custom_rom_file:
                        devicexml = DomainPcie(vmuuid).add(domain=domain, bus=bus, slot=slot, function=function, romfile=rom_file)
                    else:
                        xml = DomainPcie(vmuuid).add(domain=domain, bus=bus, slot=slot, function=function)
                    return
                except Exception as e:
                    raise HTTPException(status_code=500, detail=str(e))
            elif action == "delete":
                domain = data['domain']
                bus = data['bus']
                slot = data['slot']
                function = data['function']                   
                DomainPcie(vmuuid).remove(domain=domain, bus=bus, slot=slot, function=function)
                return
            elif action == "romfile":
                devicexml = data['xml']
                romfile = data['romfile']
                try:
                    DomainPcie(vmuuid).romfile(xml=devicexml, romfile=romfile)
                    return
                except Exception as e:
                    raise HTTPException(status_code=500, detail=str(e))
            else:
                raise HTTPException(status_code=404, detail="Action not found")

        # edit-graphics-action
        elif action.startswith("graphics"):
            action = action.replace("graphics-", "")
            if action == "add":
                graphics_type = data['type']
                try:
                    DomainGraphics(vmuuid).add(graphics_type=graphics_type)
                    return
                except Exception as e:
                    raise HTTPException(status_code=500, detail=str(e))

            elif action == "delete":
                index = data['index']
                try:
                    xml = DomainGraphics(vmuuid).remove(index=index)
                    return
                except Exception as e:
                    raise HTTPException(status_code=500, detail=str(e))
            else:
                raise HTTPException(status_code=404, detail="Action not found")

        # edit-video-action
        elif action.startswith("video"):
            action = action.replace("video-", "")
            if action == "add":
                model_type = data['type'].lower()
                try:
                    DomainVideo(vmuuid).add(model_type=model_type)
                    return
                except Exception as e:
                    raise HTTPException(status_code=500, detail=str(e))

            elif action == "delete":
                index = data['index']
                try:
                    xml = DomainVideo(vmuuid).remove(index=index)
                    return
                except Exception as e:
                    raise HTTPException(status_code=500, detail=str(e))
            else:
                raise HTTPException(status_code=404, detail="Action not found")

        elif action.startswith("sound"):
            action = action.replace("sound-", "")
            if action == "add":
                model = data['model']
                try:
                    DomainSound(vmuuid).add(model=model)
                    return
                except Exception as e:
                    raise HTTPException(status_code=500, detail=str(e))

            elif action == "delete":
                index = data['index']
                try:
                    DomainSound(vmuuid).remove(index=index)
                    return
                except Exception as e:
                    raise HTTPException(status_code=500, detail=str(e))
        else:
            raise HTTPException(status_code=404, detail="Action not found")
    
    else:
        raise HTTPException(status_code=404, detail="Action not found")


# #TODO: API-BACKUP-MANAGER
# @app.get("/api/backup-manager/configs")
# async def api_backup_manager_configs_get(username: str = Depends(check_auth)):
#     print("getting backup manager configs...")
#     configs = []
#     for config in LibvirtKVMBackup.configManager.list():
#         backups = LibvirtKVMBackup.configManager(config=config).listBackups()
#         backup_count = len(backups)
#         backup_config_data = LibvirtKVMBackup.configManager(config=config).data()
#         backup_destination = backup_config_data['Destination']
#         backup_auto_shutdown = backup_config_data['AutoShutdown']
#         backup_disks = backup_config_data['Disks']
        
#         # sort backups by latest first
#         backups.sort(key=lambda x: x['name'], reverse=True)
#         # convert item size in backups to GG
#         for backup in backups:
#             backup['size'] = storage_manager.convertSizeUnit(size=backup['size'], from_unit="B", mode="str")

#         backup_last_result = None
#         if backup_count > 0:
#             backup_last_result = backups[0]['status']
            
#         configs.append({
#             "config": config,
#             "lastResult": backup_last_result,
#             "backupCount": backup_count,
#             "destination": backup_destination,
#             "autoShutdown": backup_auto_shutdown,
#             "disks": backup_disks,
#             "backups": backups,
#         })
#     return configs

# @app.post("/api/backup-manager/configs")
# async def api_backup_manager_configs_post(request: Request, username: str = Depends(check_auth)):
#     data = await request.json()
#     try:
#         config_name = data['configName']
#         vm_name = data['vmName']
#         destination = data['destination']
#         auto_shutdown = data['autoShutdown']
#         disks = data['disks']
#     except KeyError:
#         raise HTTPException(status_code=400, detail="Missing required data")
#     try:
#         config_data = {
#             'DomainName': vm_name, 
#             'Disks': disks, 
#             'Destination': destination, 
#             'AutoShutdown': auto_shutdown
#         }
#         LibvirtKVMBackup.configManager(config=config_name).create(configdata=config_data)
#         return
#     except LibvirtKVMBackup.configError as e:
#         raise HTTPException(status_code=500, detail=str(e))

# #TODO
# ### API-BACKUP-CONFIG ###
# @app.post("/api/backup-manager/config/{config}/{action}")
# async def api_backup_manager_config_get(config: str, action: str, username: str = Depends(check_auth)):
#     if action == "delete":
#         try:
#             LibvirtKVMBackup.configManager(config=config).delete()
#             return
#         except LibvirtKVMBackup.configError as e:
#             raise HTTPException(status_code=500, detail=str(e))
#     elif action == "create-backup":
#         try:
#             print("creating backup")
#             ret =  LibvirtKVMBackup.backup(config=config)
#             if ret != 0:
#                 notification_manager.create_notification(
#                     type=NotificationType.ERROR,
#                     title="Backup Error",
#                     message=f"Backup of {config} failed. See log for details."
#                 )
#             return
#         except LibvirtKVMBackup.backupError as e:
#             raise HTTPException(status_code=500, detail=str(e))
#     else:
#         raise HTTPException(status_code=404, detail="action not found")
    

# ### API-BACKUP-ACTIONS ###
# @app.post("/api/backup-manager/{config}/{backup}/{action}")
# async def api_backup_manager_actions_post(config: str, backup: str, action: str, username: str = Depends(check_auth)):
#     if action == "log":
#         try:
#             return LibvirtKVMBackup.configManager(config).backupLog(backup)
#         except LibvirtKVMBackup.configError as e:
#             raise HTTPException(status_code=500, detail=str(e))
#     elif action == "restore":
#         try:
#             ret = LibvirtKVMBackup.restore(config=config, backup=backup)
#             if ret != 0:
#                 notification_manager.create_notification(
#                     type=NotificationType.ERROR,
#                     title="Restore Error",
#                     message=f"Restore of {config} failed. See log for details."
#                 )
#             return
#         except LibvirtKVMBackup.restoreError as e:
#             raise HTTPException(status_code=500, detail=str(e))
#     elif action == "delete":
#         try:
#             LibvirtKVMBackup.configManager(config=config).backupDelete(backup=backup)
#             return
#         except LibvirtKVMBackup.configError as e:
#             raise HTTPException(status_code=500, detail=str(e))
#     else:
#         raise HTTPException(status_code=404, detail="action not found")
    

### API-NETWORKS ###
@app.get("/api/networks")
async def api_networks_get(username: str = Depends(check_auth)):
    # get all networks from libvirt
    networks = conn.listAllNetworks()
    # create empty list for networks
    networks_list = []
    # loop through networks
    for network in networks:
        # get network xml
        network_xml = ET.fromstring(network.XMLDesc(0))            
        # get network autostart
        network_autostart = network.autostart()
        # get network active
        network_active = network.isActive()
        if network_active == 1:
            network_active = True
        else:
            network_active = False
        # get network persistent
        network_persistent = network.isPersistent()
        # create network dict
        _network = {
            "uuid": network.UUIDString(),
            "name": network.name(),
            "active": network_active,
            "persistent": network_persistent,
            "autostart": network_autostart,
            
        }
        # append network dict to networks list
        networks_list.append(_network)
    return networks_list

@app.get("/api/docker-manager/templates/{id}")
async def api_docker_manager_template_get(id: int, username: str = Depends(check_auth)):
    return dockerTemplates.getTemplate(id=id)

@app.get("/api/docker-manager/templates")
async def api_docker_manager_templates_get(username: str = Depends(check_auth)):
    return dockerTemplates.getTemplates()

@app.get("/api/docker-manager/template-locations")
async def api_docker_manager_template_locations_get(username: str = Depends(check_auth)):
    template_locations = dockerTemplates.getLocations()
    for template_location in template_locations:
        print(template_location['last_update'])
    return template_locations

@app.post("/api/docker-manager/template-locations/update")
async def api_docker_manager_template_locations_update_post(request: Request, username: str = Depends(check_auth)):
    data = await request.json()
    id = data['id']
    dockerTemplates.updateLocation(id=id)
    return

@app.put("/api/docker-manager/template-locations")
async def api_docker_manager_template_locations_put(request: Request, username: str = Depends(check_auth)):
    data = await request.json()
    id = data['id']
    name = data['name']
    url = data['url']
    branch = data['branch']
    dockerTemplates.editLocation(id=id, name=name, url=url, branch=branch)
    return

@app.delete("/api/docker-manager/template-locations")
async def api_docker_manager_template_locations_delete(request: Request, username: str = Depends(check_auth)):
    data = await request.json()
    id = data['id']
    dockerTemplates.deleteLocation(id=id)
    return

@app.post("/api/docker-manager/template-locations")
async def api_docker_manager_template_locations_post(request: Request, username: str = Depends(check_auth)):
    data = await request.json()
    name = data['name']
    url = data['url']
    branch = data['branch']
    dockerTemplates.addLocation(name=name, url=url, branch=branch)
    return

@app.get("/api/docker-manager/info")
async def api_docker_manager_info_get(username: str = Depends(check_auth)):
    return dockerGeneral.version()

@app.get("/api/docker-manager/images")
async def api_docker_manager_images_get(username: str = Depends(check_auth)):
    return dockerImages.getAll()

@app.post("/api/docker-manager/images/{action}")
async def api_docker_manager_images_post(request: Request, action: str ,username: str = Depends(check_auth)):
    data = await request.json()
    if action == "delete":
        for image in data['images']:
            image_name = image['name']
            image_tag = image['tag']
            dockerImages.remove(image_name + ":" + image_tag)
        return
    elif action == "pull":
        dockerImages.pull(image=data['image'])
    else:
        raise HTTPException(status_code=404, detail="Action not found")
    
@app.get("/api/docker-manager/containers")
async def api_docker_manager_containers_get(username: str = Depends(check_auth)):
    return dockerContainers.getAll()

@app.get("/api/docker-manager/container/{container_id}")
async def api_docker_manager_container_get(container_id: str, username: str = Depends(check_auth)):
    return dockerContainers.get(id=container_id)

@app.post("/api/docker-manager/container/{id}/{action}")
async def api_docker_manager_containers_post(request: Request, id: str, action: str ,username: str = Depends(check_auth)):
    print(f"action: {action}, id: {id}")
    if action == "start":
        dockerContainers.start(id=id)
        return
    elif action == "stop":
        dockerContainers.stop(id=id)
        return
    elif action == "restart":
        dockerContainers.restart(id=id)
        return
    elif action == "delete":
        container_data = dockerContainers().get(id=id)
        if container_data['container_type'] != "unmanaged":
            dockerContainers.delete(id=id, api_only=True)
        else:
            dockerContainers.delete(id=id)
        return
    else:
        raise HTTPException(status_code=404, detail="action not found")
    
@app.post("/api/docker-manager/containers")
async def api_docker_manager_containers_create(request: Request, username: str = Depends(check_auth)):
    data = await request.json()
    print("Request to create container: ", data)
    action = data['action']

    if action == "update":
        # Remove existing container: docker api and database
        id = data['id']
        dockerContainers.delete(id=id)

    # Create a new container
    container_name = data['name']
    container_type = data['container_type']
    container_config = data['config']
    container_webui = data['webui']
    container_command=""

    _container_image = container_config['repository'] + ':' + container_config['tag']
    _container_env = {}
    for env in container_config['env']:
        _container_env[env['name']] = env['value']
    _container_volumes = {}
    for volume in container_config['volumes']:
        # 'value' is the path on the host
        # 'bind' is the path inside the container
        _container_volumes[volume['value']] = {'bind': volume['bind'], 'mode': volume['mode']}
    for command in container_config['command']:
        container_command += command['value'] + " "
    _container_network_name = container_config['network']['name']
    _container_fixed_ip = None
    if 'ip' in container_config['network']:
        _container_fixed_ip = container_config['network']['ip']
        _container_network_config = docker_client.api.create_networking_config({
            _container_network_name: docker_client.api.create_endpoint_config(
                ipv4_address=_container_fixed_ip
            )
        })
    else:
        _container_network_config = docker_client.api.create_networking_config({
            _container_network_name: docker_client.api.create_endpoint_config()
        })

    
    print(f"image: {_container_image}")
    print(f"name: {container_name}")
    print(f"env: {_container_env}")
    print(f"volumes: {_container_volumes}")
    print(f"command: {container_command}")
    print(f"network: {_container_network_config}")
    print(f"network name: {_container_network_name}")
    print(f"fixed ip: {_container_fixed_ip}")

    # Check if the container image exists
    try:
        docker_client.images.get(_container_image)
        print("Image exists")
    except docker.errors.ImageNotFound:
        # Pull image
        print("Pulling image")
        docker_client.images.pull(_container_image)
        print("Image pulled")

    print("Creating container")
    # Create container
    docker_client_container = docker_client.api.create_container(
        image=_container_image,
        name=container_name,
        environment=_container_env,
        # volumes are the _container_volumes 
        # volumes list is from container_config['volumes']
        volumes=[volume['bind'] for volume in container_config['volumes']],
        host_config=docker_client.api.create_host_config(binds=_container_volumes),
        networking_config=_container_network_config,
        command=container_command,
        detach=True,
        tty=True,
        stdin_open=True,
    )

    print("Container created: ", docker_client_container)

    print("Adding container to database")
    # Create container in database
    dockerContainers().add(
        id=docker_client_container['Id'],
        container_type=container_type,
        webui=json.dumps(container_webui),
        config=json.dumps(container_config),
    )
    print("Container added to database")
    return

@app.get("/api/docker-manager/networks")
async def api_docker_manager_networks_get(username: str = Depends(check_auth)):
    return dockerNetworks.getAll()

@app.delete("/api/docker-manager/network/{id}")
async def api_docker_manager_networks_delete(id: str, username: str = Depends(check_auth)):
    dockerNetworks.delete(id=id)
    return

### api-host-power###
@app.post("/api/host/power/{powermsg}")
async def api_host_power_post(powermsg: str, username: str = Depends(check_auth)):
    if powermsg == "shutdown":
        shutdown_result = subprocess.run(
            ["shutdown", "-h", "now"], capture_output=True, text=True)
        if shutdown_result.returncode == 0:
            return
        else:
            raise HTTPException(status_code=500, detail=shutdown_result.stdout)
    elif powermsg == "reboot":
        global system_status
        system_status = "rebooting"
        reboot_result = subprocess.run(
            ["reboot"], capture_output=True, text=True)
        if reboot_result.returncode == 0:
            return
        else:
            system_status = "running"
            raise HTTPException(status_code=500, detail=reboot_result.stdout)
    else:
        raise HTTPException(status_code=404, detail="power action not found")

### API-STORAGE ###
@app.get("/api/storage/raid-manager")
async def api_host_storage_raid_get(username: str = Depends(check_auth)):
    try:
        return storage_manager.raid_manager.get()
    except storage_manager.StorageManagerException as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/storage/raid-manager/{action}")
async def api_host_storage_raid_post(request: Request, action: str, username: str = Depends(check_auth)):
    data = await request.json()
    if action == "create":
        try:
            storage_manager.raid_manager.create(personality=data['level'], devices=data['devices'], filesystem=data['filesystem'])
            return
        except storage_manager.StorageManagerException as e:
            raise HTTPException(status_code=500, detail=str(e))
    elif action == "delete":
        try:
            storage_manager.raid_manager.delete(path=data['path'])
            return
        except storage_manager.StorageManagerException as e:
            raise HTTPException(status_code=500, detail=str(e))
    else:
        raise HTTPException(status_code=404, detail="action not found")

@app.get("/api/storage/disks")
async def api_host_storage_disks_get(username: str = Depends(check_auth)):
    try:
        return storage_manager.disk_manager.get()
    except storage_manager.StorageManagerException as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/storage/disks/disk/{action}")
async def api_host_storage_disks_post(request: Request, action: str, username: str = Depends(check_auth)):
    data = await request.json()
    if action == "wipe":
        try:
            storage_manager.disk_manager.wipeDisk(path=data['diskpath'])
            return
        except storage_manager.StorageManagerException as e:
            raise HTTPException(status_code=500, detail=str(e))
    else:
        raise HTTPException(status_code=404, detail="action not found")

@app.post("/api/storage/disks/partition/{action}")
async def api_host_storage_disks_partition_post(request: Request, action: str, username: str = Depends(check_auth)):
    data = await request.json()
    if action == "delete":
        try:
            storage_manager.disk_manager.deletePartition(disk=data['disk'], partition=data['partition'])
            return
        except storage_manager.StorageManagerException as e:
            raise HTTPException(status_code=500, detail=str(e))
    elif action == "create":
        try:
            storage_manager.disk_manager.createPartition(diskpath=data['diskpath'], fstype=data['fstype'])
            return
        except storage_manager.StorageManagerException as e:
            raise HTTPException(status_code=500, detail=str(e))
    elif action == "mount":
        try:
            storage_manager.disk_manager.mountPartition(uuid=data['partition'], mountpoint=data['mountpoint'])
            return
        except storage_manager.StorageManagerException as e:
            raise HTTPException(status_code=500, detail=str(e))
    elif action == "unmount":
        try:
            storage_manager.disk_manager.unmountPartition(uuid=data['partition'])
            return
        except storage_manager.StorageManagerException as e:
            raise HTTPException(status_code=500, detail=str(e))
    elif action == "format":
        try:
            storage_manager.disk_manager.formatPartition(path=data['partition'], fstype=data['fstype'])
            return
        except storage_manager.StorageManagerException as e:
            raise HTTPException(status_code=500, detail=str(e))
    else:
        raise HTTPException(status_code=404, detail="action not found")
    
@app.get("/api/storage/sharedfolders")
async def api_host_storage_sharedfolders_get(username: str = Depends(check_auth)):
    try:
        return storage_manager.shared_folders.get()
    except storage_manager.StorageManagerException as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/api/storage/sharedfolders/availabledevices")
async def api_host_storage_sharedfolders_availabledevices_get(username: str = Depends(check_auth)):
    try:
        return storage_manager.shared_folders.getAvailableDevices()
    except storage_manager.StorageManagerException as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/api/storage/sharedfolders/{action}")
async def api_host_storage_sharedfolders_post(request: Request, action: str, username: str = Depends(check_auth)):
    data = await request.json()
    if action == "create":
        try:
            storage_manager.shared_folders.create(name=data['name'], target=data['target'])
            return
        except storage_manager.StorageManagerException as e:
            raise HTTPException(status_code=500, detail=str(e))
    elif action == "delete":
        try:
            storage_manager.shared_folders.remove(name=data['name'])
            return
        except storage_manager.StorageManagerException as e:
            raise HTTPException(status_code=500, detail=str(e))
    elif action == "smb-edit":
        name = data['name']
        smb_status = data['status']
        if smb_status == False:
            if storage_manager.shared_folders.getSmbShare(name=name) is not None:
                storage_manager.shared_folders.removeSMBShare(name=name)
            return
        else:
            if storage_manager.shared_folders.getSmbShare(name=name) is not None:
                storage_manager.shared_folders.removeSMBShare(name=name)
            smb_mode = data['mode']
            smb_path = data['path']
            if smb_mode == "PUBLIC":
                storage_manager.shared_folders.createSMBShare(name=name, path=smb_path, mode="PUBLIC")
            elif smb_mode == "PRIVATE":
                smb_users = data['users']
                users_list = []
                users_write_list = []
                users_read_list = []
                for user in smb_users:
                    users_list.append(user['name'])
                    if user['mode'] == "rw":
                        users_write_list.append(user['name'])
                        users_read_list.append(user['name'])
                    elif user['mode'] == "ro":
                        users_read_list.append(user['name'])
                storage_manager.shared_folders.createSMBShare(
                    name=name, 
                    path=smb_path, 
                    mode="PRIVATE",
                    users_list=users_list,
                    users_write_list=users_write_list,
                    users_read_list=users_read_list
                )
            elif smb_mode == "SECURE":
                smb_users = data['users']
                users_write_list = []
                for user in smb_users:
                    if user['mode'] == "rw":
                        users_write_list.append(user['name'])
                storage_manager.shared_folders.createSMBShare(
                    name=name, 
                    path=smb_path, 
                    mode="SECURE",
                    users_write_list=users_write_list
                )
                return
    else:
        raise HTTPException(status_code=404, detail="action not found")

@app.get("/api/host/system-info/{action}")
async def api_system_info_get(action: str, username: str = Depends(check_auth)):
    if action == "all":
        sysInfo = ET.fromstring(conn.getSysinfo(0))
        # if baseboard exists in sysinfo
        baseboard_manufacturer = "Unknown"
        baseboard_product = ""
        baseboard_version = ""
        if sysInfo.find("baseBoard") is not None:
            baseboard_manufacturer = sysInfo.find("baseBoard/entry[@name='manufacturer']").text
            baseboard_product = sysInfo.find("baseBoard/entry[@name='product']").text
            baseboard_version = sysInfo.find("baseBoard/entry[@name='version']").text
        processor_version = sysInfo.find("processor/entry[@name='version']").text
        memory_size = 0
        for memory_device in sysInfo.findall("memory_device"):
            memory_size = int(memory_size) + int(memory_device.find("entry[@name='size']").text.replace(" GB", ""))
        memory_size = str(memory_size) + " GB"
        uptime = humanize.precisedelta(datetime.now() - datetime.fromtimestamp(psutil.boot_time()), minimum_unit="minutes", format="%0.0f")
        return {
            "motherboard": baseboard_manufacturer + " " + baseboard_product + " " + baseboard_version,
            "processor": processor_version,
            "memory": memory_size,
            "os": distro.name(pretty=True),
            "hostname": conn.getHostname(),
            "linuxVersion": os.uname()[2],
            "uptime": uptime,
        }
    elif action == "hostname":
        return {
            "hostname": conn.getHostname()
        }
    elif action == "guest-machine-types":
        return getGuestMachineTypes()
    else:
        raise HTTPException(status_code=404, detail="action not found")

@app.post("/api/host/system-info/{action}")
async def api_system_info_hostname_post(action: str, hostname: str = Form(...), username: str = Depends(check_auth)):
    if action == "hostname":
        # Run hostnamectl set-hostname
        hostname_result = subprocess.run(
            ["hostnamectl", "set-hostname", hostname], capture_output=True, text=True)
        if hostname_result.returncode == 0:
            return
        else:
            raise HTTPException(status_code=500, detail=hostname_result.stdout)
    else:
        raise HTTPException(status_code=404, detail="action not found")
    
# API-SYSTEM-USERS
@app.get("/api/system/users")
async def api_system_users_get(username: str = Depends(check_auth)):
    users = []
    for user in pwd.getpwall():
        # list users with UID >= 1000 and <= 60000 or UID == 0
        if user.pw_uid >= 1000 and user.pw_uid <= 60000 or user.pw_uid == 0:
            smb_user = storage_manager.smbusers.lookup(name=user.pw_name)
            users.append({
                "name": user.pw_name,
                "smb_user": smb_user,
                "uid": user.pw_uid,
                "gid": user.pw_gid,
                "home": user.pw_dir,
                "shell": user.pw_shell,
                "groups": [group.gr_name for group in grp.getgrall() if user.pw_name in group.gr_mem],
            })
    return users

@app.post("/api/system/users/change-password")
async def api_system_users_change_password(request: Request, username: str = Depends(check_auth)):
    data = await request.json()
    username = data['username']
    password = data['password']
    try:
        subprocess.check_output(["passwd", username, "--stdin"], input=password.encode())
        return
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=e)
    
@app.post("/api/system/users/remove-user")
async def api_system_users_remove_user(request: Request, username: str = Depends(check_auth)):
    data = await request.json()
    username = data['username']
    try:
        subprocess.check_output(["userdel", username])
        return
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=e)

@app.post("/api/system/users/change-smb-password")
async def api_system_users_change_smb_password(request: Request, username: str = Depends(check_auth)):
    data = await request.json()
    username = data['username']
    password = data['password']
    try:
        storage_manager.smbusers.reset_password(username, password)
        return
    except storage_manager.StorageManagerException as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/system/users/remove-smb-user")
async def api_system_users_remove_smb_user(request: Request, username: str = Depends(check_auth)):
    data = await request.json()
    username = data['username']
    try:
        if storage_manager.smbusers.lookup(name=username) is not None:
            storage_manager.smbusers.delete(name=username)
        return
    except storage_manager.StorageManagerException as e:
        raise HTTPException(status_code=500, detail=str(e))

### API-SYSTEM-FILE-MANAGER ###
@app.post("/api/system/file-manager")
async def api_system_file_manager_get(request: Request, username: str = Depends(check_auth)):
    data = await request.json()
    path = data['path']
    if os.path.isdir(path):
        parent_dir = os.path.abspath(os.path.join(path, os.pardir))
        files = []
        if path != "/":
            files.append({
                "name": "..",
                "parentdir": parent_dir,
                "path": parent_dir,
                "type": "dirparent",
                "size": "",
                "permissions": "",
                "modified": "",
            })
        for file in os.listdir(path):
            file_path = os.path.join(path, file)
            file_type = "file"
            file_size = ""
            if os.path.isdir(file_path):
                file_type = "dir"
            else:
                # calculate size of file if path is not a directory. ConvertSizeUnit returns a tuple with the size and the unit
                file_size = storage_manager.convertSizeUnit(size=os.path.getsize(file_path), from_unit="B", mode="str")

            file_modified = datetime.fromtimestamp(os.path.getmtime(file_path)).strftime("%Y-%m-%d %H:%M:%S")
            file_permissions = oct(os.stat(file_path).st_mode)[-3:]


            files.append({
                "name": file,
                "path": file_path,
                "type": file_type,
                "size": file_size,
                "permissions": file_permissions,
                "modified": file_modified,
            })
        return { "list": files, "path": path }
    else:
        raise HTTPException(status_code=404, detail="Path not found")
    
@app.post("/api/system/file-manager/{action}")
async def api_system_file_manager_action(action: str, request: Request, username: str = Depends(check_auth)):
    data = await request.json()
    if action == "remove":
        path = data['path']
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.remove(path=path)
    elif action == "create-folder":
        name = data['name']
        path = data['path']
        new_path = os.path.join(path, name)
        os.makedirs(new_path)
    elif action == "rename":
        name = data['name']
        path = data['path']
        new_path = os.path.join(os.path.dirname(path), name)
        os.rename(path, new_path)
    elif action == "validate-path":
        path = data['path']
        # if directory, return dir, if file return file, if not found return not found
        if os.path.isdir(path):
            return JSONResponse(content={"type": "dir"})
        elif os.path.isfile(path):
            parent = os.path.dirname(path)
            return JSONResponse(content={"type": "file", "parent": parent})
        else:
            raise HTTPException(status_code=500, detail="not found")
    else:
        raise HTTPException(status_code=404, detail="Action not found")

### API-HOST-SYSTEM-DEVICES ###
@app.get("/api/host/system-devices/{devicetype}")
async def api_host_system_devices_get(devicetype: str, username: str = Depends(check_auth)):
    if devicetype == "pcie":
        return HostPcieDevices()
    elif devicetype == "usb":
        return SystemUsbDevicesList()
    else:
        raise HTTPException(status_code=404, detail="Device type not found")

### API-HOST-SETTINGS-ACTIONS ###
@app.get("/api/host/settings/{action}")
async def api_host_settings_get(action: str, username: str = Depends(check_auth)):
    if action == "all":
        return settings().getAll()
    elif action == "vnc":
        vnc_settings = { 
            "port": settings().get("novnc port"), 
            "protocool": settings().get("novnc protocool"), 
            "path": settings().get("novnc path"),
            "ip": settings().get("novnc ip")
        }
        return vnc_settings
    else:
        raise HTTPException(status_code=404, detail="Action not found")
    
@app.post("/api/host/settings/{action}")
async def api_host_settings_post(request: Request, action: str, username: str = Depends(check_auth)):
    if action == "edit":
        data = await request.json()
        setting = data['setting']
        value = data['value']
        settings().set(setting, value)
        return
    
@app.get("/api/vm-manager/settings/ovmf-paths/{action}")
async def api_vm_manager_settings_ovmf_paths_get(action: str, username: str = Depends(check_auth)):
    if action == "all":
        return settings_ovmfpaths().getAll()
    
@app.post("/api/vm-manager/settings/ovmf-paths/{action}")
async def api_vm_manager_settings_ovmf_paths_post(request: Request, action: str, username: str = Depends(check_auth)):
    data = await request.json()
    name = data['name']
    if action == "edit":
        path = data['path']
        settings_ovmfpaths().set(name, path)
        return
    elif action == "delete":
        settings_ovmfpaths().delete(name)
        return
    elif action == "add":
        path = data['path']
        settings_ovmfpaths().add(name, path)
        return
    else:
        raise HTTPException(status_code=404, detail="Action not found")

### API-NOTIFICATIONS ###
@app.get("/api/notifications")
async def api_notifications_get(username: str = Depends(check_auth)):
    print("get notifications")
    return notification_manager.get_notifications()

@app.delete("/api/notifications/{id}")
async def api_notifications_delete(id: int, username: str = Depends(check_auth)):
    if id == -1:
        notification_manager.delete_all_notifications()
    else:
        notification_manager.delete_notification(id)
    return

@app.post("/api/notifications")
async def api_notifications_post(request: Request, username: str = Depends(check_auth)):
    data = await request.json()
    for notification in data:
        notification_type = notification['type']
        if notification_type == "error":
            notification_type = NotificationType.ERROR
        elif notification_type == "warning":
            notification_type = NotificationType.WARNING
        elif notification_type == "success":
            notification_type = NotificationType.SUCCESS
        else:
            notification_type = NotificationType.INFO
        
        notification_title = notification['title']
        notification_message = notification['message']
        notification_manager.create_notification(
            type = notification_type,
            title = notification_title,
            message = notification_message,
        )
    
    return
