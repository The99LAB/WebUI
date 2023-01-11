from flask import Flask, render_template, jsonify, request, redirect, session
from flask_cors import CORS, cross_origin
from flask_restful import reqparse, abort, Api, Resource
import psutil
import libvirt
from xml.etree import ElementTree as ET
from time import sleep
import re
import os
import json
from string import ascii_lowercase
from flask_socketio import SocketIO, Namespace, emit
import subprocess
import usb.core

"""
NOTE: Start websocket: websockify -D --web=/usr/share/novnc/ 6080 --target-config /home/stijnrombouts/token.list
"""

class CustomFlask(Flask):
    jinja_options = Flask.jinja_options.copy()
    jinja_options.update(dict(
        variable_start_string='%%',
        variable_end_string='%%',
    ))
app = CustomFlask(__name__, static_url_path='')
CORS(app, resources={r"*": {"origins": "*"}})
api = Api(app)
socketio = SocketIO(app, cors_allowed_origins="*")
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

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

            if domain.isActive() == True:
                # if domain is active > search for VNC port > set token to the correct port
                vmXml = domain.XMLDesc(0)
                root = ET.fromstring(vmXml)
                graphics = root.find('./devices/graphics')
                try:
                    vncport = graphics.get('port')
                    vnc_state = True
                    try: 
                        with open("/home/stijn/token.list", "w") as tokenlist:
                            tokenlist.write(f"{dom_uuid}: localhost:{vncport}")
                    except Exception:
                        print("Couldn't read the token file") 
                except Exception:
                    vncport = "none"
                    vnc_state = False
            else:
                vncport = "none"
                vnc_state = False
 
            # result = [dom_name, dom_state, vncport, dom_uuid]
            dom_memory_unit = "GB"
            dom_memory_stat = vmmemory(dom_uuid).current(dom_memory_unit)
            dom_memory_min = dom_memory_stat[0]
            dom_memory_max = dom_memory_stat[1]
            result = {
                "uuid": dom_uuid,
                "name": dom_name,
                "memory_min": dom_memory_min,
                "memory_max": dom_memory_max,
                "memory_unit": "GB",
                "vcpus": 2,
                "state": dom_state,
                "VNC": vnc_state,
            }
            results.append(result)
    else:
        results = None
    return results

def getRunningDomains():
    runningDomains = conn.listAllDomains(1)
    results = []
    if len(runningDomains) != 0:
        for domain in runningDomains:
            dom_name = domain.name()
            dom_uuid = domain.UUIDString()
            result = [dom_name, dom_uuid]
            results.append(result)
    return results

class vmmemory():
    def __init__(self, uuid):
        self.domain = conn.lookupByUUIDString(uuid)

    def current(self, unit):
        maxmem = self.domain.info()[1]
        minmem = self.domain.info()[2]
        if unit == "TB":
            maxmem = maxmem / 1024 / 1024 / 1024
            minmem = minmem / 1024 / 1024 / 1024
        elif unit == "GB":
            maxmem = maxmem / 1024 / 1024
            minmem = minmem / 1024 / 1024
        elif unit == "MB":
            maxmem = maxmem / 1024
            minmem = minmem / 1024
        elif unit == "KB":
            maxmem = maxmem
            minmem = minmem   
        else:
            return("Error: Unknown unit for memory size") 
        return [int(minmem), int(maxmem)]

    def edit(self, minmem, minmemunit, maxmem, maxmemunit):
        maxmem = int(maxmem)
        minmem = int(minmem)
        if minmemunit == "TB":
            minmem = minmem * 1024 * 1024 * 1024
        elif minmemunit == "GB":
            minmem = minmem * 1024 * 1024
        elif minmemunit == "MB":
            minmem = minmem * 1024
        elif minmemunit == "KB":
            minmem = minmem   
        else:
            return("Error: Unknown unit for minmemory size") 

        if maxmemunit == "TB":
            maxmem = maxmem * 1024 * 1024 * 1024
        elif maxmemunit == "GB":
            maxmem = maxmem * 1024 * 1024
        elif maxmemunit == "MB":
            maxmem = maxmem * 1024
        elif maxmemunit == "KB":
            maxmem = maxmem
        else:
            return("Error: Unknown unit for maxmemory size") 

        if minmem > maxmem:
            return("Error: minmemory can't be bigger than maxmemory")

        else:    
            vmXml = self.domain.XMLDesc(0)
            try:
                currentminmem = (re.search("<currentMemory unit='KiB'>[0-9]+</currentMemory>", vmXml).group())
                currentmaxmem = (re.search("<memory unit='KiB'>[0-9]+</memory>", vmXml).group())
                try:
                    output = vmXml
                    output = output.replace(currentmaxmem, "<memory unit='KiB'>"+ str(maxmem) + "</memory>")
                    output = output.replace(currentminmem, "<currentMemory unit='KiB'>"+ str(minmem) + "</currentMemory>")
                    try:
                        conn.defineXML(output)
                        return('Succeed')
                    except libvirt.libvirtError as e:
                        return(f'Error:{e}')
                except:
                    return("failed to replace minmemory and/or maxmemory!")    
            except:
                return("failed to find minmemory and maxmemory in xml!")

class getmemory():
    def __init__(self):
        self.systemmem = psutil.virtual_memory().total
    def systemmem(self):
        return self.systemmem
    def vmeditsizes(self):
        times = self.systemmem/1024/1024/512
        sizes = []
        currentsize = 512
        for i in range(round(times)):
            sizes.append(currentsize)
            currentsize = currentsize + 512
        return sizes

class cpu():
    def __init__(self, uuid):
        self.domain = conn.lookupByUUIDString(uuid)
        self.vmXml = self.domain.XMLDesc(0)

    def get(self):
        maxvcpu = self.domain.vcpusFlags(libvirt.VIR_DOMAIN_VCPU_MAXIMUM)
        currentvcpu = self.domain.vcpusFlags(libvirt.VIR_DOMAIN_AFFECT_CURRENT)
        #TODO: Get sockets, cores, threads

        root = ET.fromstring(self.vmXml)
        cpu = root.find('./cpu')
        cpumode = cpu.get('mode')

        topology = cpu.find("./topology")
        if topology != None:
            sockets = topology.get('sockets')
            cores = topology.get('cores')
            threads = topology.get('threads')
        else:
            sockets = maxvcpu
            cores = 1
            threads = 1

        return [currentvcpu, maxvcpu, cpumode, sockets, cores, threads]

    def set(self, customtopology, currentvcpu, maxvcpu, cpumode, sockets="", cores="", threads=""):
        output = self.vmXml

        cpusfindtring = re.search("(<cpu.*/>|<cpu(.|\n)*</cpu>)", self.vmXml).group()
        vcpufindstring = re.search("<vcpu.*</vcpu>", self.vmXml).group()

        if currentvcpu != maxvcpu:
            print("not same")
            output = output.replace(vcpufindstring, f"<vcpu placement='static' current='{currentvcpu}'>{maxvcpu}</vcpu>")
        else:
            output = output.replace(vcpufindstring, f"<vcpu placement='static'>{maxvcpu}</vcpu>")

        if cpumode == "host-passthrough":
            migratable = "migratable='on'"
        else:
            migratable = ""

        if customtopology == True:
            cpusreplacetring = f"<cpu mode='{cpumode}' check='partial' {migratable}><topology sockets='{sockets}' dies='1' cores='{cores}' threads='{threads}'/></cpu>"
        elif customtopology == False:
            cpusreplacetring = f"<cpu mode='{cpumode}' check='partial' {migratable}/>"
        else:
            return "Error: costomcputopology is not set correctly!"

        output = output.replace(cpusfindtring, cpusreplacetring)

        try:
            conn.defineXML(output)
            return 'Succeed'

        except libvirt.libvirtError as e:
            return f'Error: {e}'

class storage():
    def __init__(self, domain_uuid):
        self.domain_uuid = domain_uuid
        self.domain = conn.lookupByUUIDString(domain_uuid)
        self.vmXml = self.domain.XMLDesc(0)
    def get(self):
        tree=ET.fromstring(self.vmXml)
        disks = tree.findall('./devices/disk')
        disklist = []
        for index, i in enumerate(disks):
            devicetype = i.get('device')
            drivertype = i.find('./driver').get('type')

            source = i.find('./source')
            if source != None:
                sourcefile = source.get('file')
            else:
                sourcefile = "Not set"

            target = i.find('./target')
            busformat = target.get('bus')

            readonlyelem = i.find('./readonly')
            if readonlyelem != None:
                readonly = True
            else:
                readonly = False
            disknumber = index
            xml = ET.tostring(i).decode()
            disk = [disknumber, devicetype, drivertype, busformat, sourcefile, readonly, xml]
            disklist.append(disk)
        return disklist

    def remove(self, disknumber):
        tree=ET.fromstring(self.vmXml)
        for idx, disk in enumerate(self.get()):
            if idx == int(disknumber):
                try:
                    self.domain.detachDeviceFlags(disk[6], libvirt.VIR_DOMAIN_AFFECT_CONFIG)
                    return 'Succeed'
                except libvirt.libvirtError as e:
                    return f'Error: {e}'
                break    

    def add_xml(self, targetbus, devicetype, sourcefile, drivertype, readonly="", bootorder=None):
        tree=ET.fromstring(self.vmXml)
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
            index=0
        if targetbus == "sata" or targetbus == "scsi" or targetbus == "usb":
            FreeTargetDev = "sd" + ascii_lowercase[index]
        elif targetbus == "virtio":
            FreeTargetDev = "vd" + ascii_lowercase[index]

        if readonly == "":
            if devicetype == "cdrom":
                readonlystate = True
            else:
                readonlystate = False
        elif readonly == "on":
            readonlystate = True
        elif readonly == "off":
            readonlystate = False
        else:
            return "Error: unknown readonly state"

        # create boot order string
        bootorderstring = ""
        if bootorder != None:
            bootorderstring = f"<boot order='{str(bootorder)}'/>"

        # add the disk to xml
        diskxml = f"""<disk type='file' device='{devicetype}'>
        <driver name='qemu' type='{drivertype}'/>
        <source file='{sourcefile}'/>
        <target dev='{FreeTargetDev}' bus='{targetbus}'/>
        {bootorderstring}
        {"<readonly/>" if readonlystate else ""}
        </disk>"""
        return diskxml

    def add(self, targetbus, devicetype, sourcefile, drivertype, readonly="", bootorder=None):
        diskxml = self.add_xml(targetbus=targetbus, devicetype=devicetype, sourcefile=sourcefile, drivertype=drivertype, readonly=readonly, bootorder=bootorder)
        try:
            self.domain.attachDeviceFlags(diskxml, libvirt.VIR_DOMAIN_AFFECT_CONFIG)
            return 'Succeed'
        except libvirt.libvirtError as e:
            return f'Error: {e}'

    def createnew(self, pooluuid, disksize, disksizeunit, disktype, diskbus, bootorder=None):
        volumename = poolStorage(pooluuid).getUnusedVolumeName(self.domain_uuid, disktype)
        pool = conn.storagePoolLookupByUUIDString(pooluuid)

        if disksizeunit == "TB":
            disksize = int(disksize) * 1024 * 1024 * 1024 * 1024
        elif disksizeunit == "GB":
            disksize = int(disksize) * 1024 * 1024 * 1024
        elif disksizeunit == "MB":
            disksize = int(disksize) * 1024 * 1024
        elif disksizeunit == "KB":
            disksize = int(disksize) * 1024
        else:
            return f"Error: Unsupported disk size unit"

        diskxml = f"""<volume>
        <name>{volumename}</name>
        <capacity>{disksize}</capacity>
        <allocation>0</allocation>
        <target>
            <format type="{disktype}"/>
        </target>
        </volume>"""

        try:
            pool.createXML(diskxml)
        except libvirt.libvirtError as e:
            return f"Error: Creating volume on pool with uuid: {pooluuid} failed with error: {e}" 
        
        volumepath = poolStorage(pooluuid).getVolumePath(volumename)
        adddisk = storage(self.domain_uuid).add(diskbus, "disk", volumepath, disktype, bootorder=bootorder)
        if adddisk != "Succeed":
            return f"Error adding disk: {adddisk}"
        else:
            return "Succeed"

class poolStorage():
    def __init__ (self, pooluuid):
        self.pooluuid = pooluuid

    def getUnusedVolumeName(self, vmuuid, vdisktype):
        domainName = conn.lookupByUUIDString(vmuuid).name()
        volname = f"{domainName}.{vdisktype}"
        sp = conn.storagePoolLookupByUUIDString(self.pooluuid) 
        stgvols = sp.listVolumes()

        count = 0
        while True:
            if volname in stgvols:
                count +=1
                volname = f"{domainName}-{count}.{vdisktype}"
            else: 
                break
        return volname

    @classmethod
    @property
    def list(self):
        pools = conn.listAllStoragePools()
        poollist = []
        for pool in pools:
            info = pool.info()
            name = pool.name()
            uuid = pool.UUIDString()
            if pool.autostart() == 1:
                autostart = "Yes"
            else:
                autostart = "No"

            if pool.isActive() == 1:
                active = "Yes"
            else:
                active = "No"        

            capacity = str(round(info[1] / 1024 / 1024 / 1024)) + "GB"
            allocation = str(round(info[2] / 1024 / 1024 / 1024)) + "GB"
            available = str(round(info[3] / 1024 / 1024 / 1024)) + "GB"

            poolinfo = [name, uuid, autostart, active, capacity, allocation, available]
            poollist.append(poolinfo)
        return poollist

    def getVolumePath(self, poolvolume):
        pool = conn.storagePoolLookupByUUIDString(self.pooluuid)
        definedxml = pool.storageVolLookupByName(poolvolume).XMLDesc()
        root = ET.fromstring(definedxml)
        key = root.find('key')
        voluempath = key.text
        return voluempath

def UsbDevicesList():
    devices = usb.core.find(find_all=True)
    deviceslist = []
    for device in devices:
        manufacturer = device.manufacturer
        product = device.product
        vendorid = hex(device.idVendor)
        productid = hex(device.idProduct)
        if vendorid !="0x1d6b":
            devicelist = [manufacturer, product, vendorid, productid]
            deviceslist.append(devicelist)
    return deviceslist      

def SystemPciDevices():
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
                productName = ""
            vendor = root.find('./capability/vendor')
            vendorid = vendor.get('id')
            vendorName = vendor.text
            iommuGroup = root.find('./capability/iommuGroup').get('number')
            capability = root.find('./capability')
            domain = capability.find('domain').text
            bus = capability.find('bus').text
            slot = capability.find('slot').text
            function = capability.find('function').text
            try:
                driver = root.find('./driver/name').text
            except AttributeError:
                driver = ""    
            pcidevicesList.append([int(iommuGroup), path, productName, productid, vendorName, vendorid, driver, domain, bus, slot, function])
        except AttributeError:
            pass
    pcidevicesList.sort()
    return pcidevicesList

class DomainPci():
    def __init__(self, vmuuid):
        self.domain = conn.lookupByUUIDString(vmuuid)
        self.vmXml = self.domain.XMLDesc()
        
    def get(self):
        tree = ET.fromstring(self.vmXml)
        pcidevices = []
        hostdevs = tree.findall('./devices/hostdev')
        for hostdev in hostdevs:
            foundSystemPciDevice = False
            hostdevtype = hostdev.get('type')
            if hostdevtype == 'pci':
                source_address = hostdev.find('source/address')
                domain = int(source_address.get('domain'), 0)
                bus = int(source_address.get('bus'), 0)
                slot = int(source_address.get('slot'), 0)
                function = int(source_address.get('function'), 0)

                for i in SystemPciDevices():
                    systempcidomain = int(i[7])
                    systempcibus = int(i[8])
                    systempcislot = int(i[9])
                    systempcifunction = int(i[10])
                    deviceProductName = i[2]
                    deviceVendorName = i[4]
                    devicepath = i[1]

                    if systempcidomain == domain and systempcibus == bus and systempcislot == slot and systempcifunction == function:
                        foundSystemPciDevice = True
                        break
                if foundSystemPciDevice:
                    pcidevices.append([devicepath, domain, bus, slot, function, deviceProductName, deviceVendorName])
                else:
                    pcidevices.append(["Unkonwn", domain, bus, slot, function, "Unkown", "Unknown"])
    
        return pcidevices

    def remove(self, argdomain, argbus, argslot, argfunction):
        tree = ET.fromstring(self.vmXml)
        hostdevs = tree.findall('./devices/hostdev')
        for hostdev in hostdevs:
            hostdevtype = hostdev.get('type')
            if hostdevtype == 'pci':
                source_address = hostdev.find('source/address')
                xmldomain = int(source_address.get('domain'), 0)
                xmlbus = int(source_address.get('bus'), 0)
                xmlslot = int(source_address.get('slot'), 0)
                xmlfunction = int(source_address.get('function'), 0)

                if xmldomain == argdomain and xmlbus == argbus and xmlslot == argslot and xmlfunction == argfunction:
                    print("MATCH")
                    pcidevicexml = ET.tostring(hostdev).decode()
                    try:
                        self.domain.detachDeviceFlags(pcidevicexml, libvirt.VIR_DOMAIN_AFFECT_CONFIG)
                        return 'Succeed'
                    except libvirt.libvirtError as e:
                        return f'Error: {e}'

    def add(self, argdomain, argbus, argslot, argfunction):
        pcidevicexml = f"<hostdev mode='subsystem' type='pci' managed='yes'><source><address domain='{argdomain}' bus='{argbus}' slot='{argslot}' function='{argfunction}'/></source></hostdev>"
        try:
            self.domain.attachDeviceFlags(pcidevicexml, libvirt.VIR_DOMAIN_AFFECT_CONFIG)
            return 'Succeed'
        except libvirt.libvirtError as e:
            return f'Error: {e}'  

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

                for i in UsbDevicesList():
                    systemusbproductid = i[3]
                    systemusbvendorid = i[2]
                    manufacturer = i[0]
                    product = i[1]

                    if int(systemusbvendorid, 0) == int(vendorid, 0) and int(systemusbproductid, 0) == int(productid, 0):
                        foundSystemUsbDevice = True
                        break
                if foundSystemUsbDevice:
                    usbdevices.append([manufacturer, product, vendorid, productid])
                else:
                    usbdevices.append(["Unkonwn", "Unknown", vendorid, productid])
        return usbdevices

    def add(self, vendorid, productid):
        xml = f"<hostdev mode='subsystem' type='usb' managed='no'><source><vendor id='{vendorid}'/><product id='{productid}'/></source></hostdev>"
        try:
            self.domain.attachDeviceFlags(xml, libvirt.VIR_DOMAIN_AFFECT_CONFIG)
            return 'Succeed'
        except libvirt.libvirtError as e:
            return f"Error: {e}"
    def remove(self, vendorid, productid):
        xml = f"<hostdev mode='subsystem' type='usb' managed='no'><source><vendor id='{vendorid}'/><product id='{productid}'/></source></hostdev>"
        try:
            self.domain.detachDeviceFlags(xml, libvirt.VIR_DOMAIN_AFFECT_CONFIG)
            return 'Succeed'
        except libvirt.libvirtError as e:
            return f"Error: {e}"

class domainNetworkInterface():
    def __init__(self, dom_uuid):
        self.domain = conn.lookupByUUIDString(dom_uuid)
        self.domainxml = self.domain.XMLDesc()
    
    def get(self):
        networkinterfaces = []
        tree = ET.fromstring(self.domainxml)
        interfaces = tree.findall('./devices/interface')
        for index, interface in enumerate(interfaces):
            xml = ET.tostring(interface).decode()
            if interface.get('type') == "network":
                mac_addr = interface.find("mac").get('address')
                source_network = interface.find("source").get('network')
                model = interface.find('model').get("type")
                networkinterfaces.append([index, xml, mac_addr, source_network, model])
        return networkinterfaces
    
    def remove(self, index):
        for idx, interface in enumerate(self.get()):
            if idx == int(index):
                return interface[1]

class create_vm():
    def __init__(self, name, machine_type, bios_type, mem_min, mem_min_unit, mem_max, mem_max_unit, disk=False, disk_size=None, disk_size_unit=None, disk_type=None, disk_bus=None, disk_pool=None, iso=False, iso_pool=None, iso_file=None, network=False, network_source=None, network_model=None):
        self.name = name
        self.machine_type = machine_type
        self.bios_type = bios_type
        self.mem_min = mem_min
        self.min_mem_unit = mem_min_unit
        self.mem_max = mem_max
        self.max_mem_unit = mem_max_unit
        self.disk = disk
        self.disk_size = disk_size
        self.disk_size_unit = disk_size_unit
        self.disk_type = disk_type
        self.disk_bus = disk_bus
        self.disk_pool = disk_pool
        self.iso = iso
        self.iso_pool = iso_pool
        self.iso_file = iso_file
        self.network = network
        self.network_source = network_source
        self.network_model = network_model        

    def win10(self):
        if self.min_mem_unit == "MB":
            mem_min = int(self.mem_min)
        elif self.min_mem_unit == "GB":
            mem_min = int(self.mem_min) * 1024
        elif self.min_mem_unit == "TB":
            mem_min = int(self.mem_min) * 1024 * 1024
        if self.max_mem_unit == "MB":
            mem_max = int(self.mem_max)
        elif self.max_mem_unit == "GB":
            mem_max = int(self.mem_max) * 1024
        elif self.max_mem_unit == "TB":
            mem_max = int(self.mem_max) * 1024 * 1024    

        ovmfstring = "<loader readonly='yes' type='pflash'>/usr/share/OVMF/OVMF_CODE_4M.fd</loader>"
        
        if self.network:
            networkstring = f"<interface type='network'><source network='{self.network_source}'/><model type='{self.network_model}'/></interface>"
        
        if self.iso:
            isopath = poolStorage(pooluuid=self.iso_pool).getVolumePath(poolvolume=self.iso_file)
            createisoxml = f"""<disk type='file' device='cdrom'>
                            <driver name='qemu' type='raw'/>
                            <source file='{isopath}'/>
                            <target dev='sda' bus='sata'/>
                            <boot order='2'/>
                            "<readonly/>
                            </disk>"""

        if self.disk_size_unit == "TB":
            disk_size = int(self.disk_size) * 1024 * 1024 * 1024 * 1024
        elif self.disk_size_unit == "GB":
            disk_size = int(self.disk_size) * 1024 * 1024 * 1024
        elif self.disk_size_unit == "MB":
            disk_size = int(self.disk_size) * 1024 * 1024
        elif self.disk_size_unit == "KB":
            disk_size = int(self.disk_size) * 1024

        if self.disk:
            pool = conn.storagePoolLookupByUUIDString(self.iso_pool)
            disk_volume_name = f"{self.name}-0.{self.disk_type}"
            diskxml = f"""<volume>
            <name>{disk_volume_name}</name>
            <capacity>{disk_size}</capacity>
            <allocation>0</allocation>
            <target>
                <format type="{self.disk_type}"/>
            </target>
            </volume>"""
            pool.createXML(diskxml)
            diskvolumepath = poolStorage(self.disk_pool).getVolumePath(disk_volume_name)
            creatediskxml = f"""<disk type='file' device='disk'>
                            <driver name='qemu' type='{self.disk_type}'/>
                            <source file='{diskvolumepath}'/>
                            <target dev='{"vda" if self.disk_bus == "virtio" else "sdb"}' bus='{self.diskbus}'/>
                            <boot order='1'/>
                            </disk>"""
            

        self.xml = f"""<domain type='kvm'>
        <name>{self.name}</name>
        <metadata>
            <libosinfo:libosinfo xmlns:libosinfo="http://libosinfo.org/xmlns/libvirt/domain/1.0">
            <libosinfo:os id="http://microsoft.com/win/10"/>
            </libosinfo:libosinfo>
        </metadata>
        <memory unit='KiB'>{mem_max}</memory>
        <currentMemory unit='KiB'>{mem_min}</currentMemory>
        <vcpu>2</vcpu>
        <os>
            <type arch='x86_64' machine='{self.machine_type}'>hvm</type>
            {ovmfstring if self.bios_type == "ovmf" else ""}
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
            <emulator>/usr/bin/qemu-system-x86_64</emulator>
            {networkstring if self.network == "yes" else ""}
            {createisoxml if self.iso == "existing" else ""}
            {creatediskxml if self.disk == "new" else ""}
            <graphics type='vnc' port='-1'/>
            <video>
            <model type='qxl'/>
            </video>
        </devices>
        </domain>"""

    def create(self):
        conn.defineXML(self.xml)

# fakevm_results = [{
#     "uuid": "1",
#     "name": "win10",
#     "memory": "4096",
#     "vcpus": "8",
#     "state": 'Shutdown', 
#     "VNC": True
# },
#     {
#     "uuid": "2",
#     "name": "macOS-Ventura",
#     "memory": "8192",
#     "vcpus": "4",
#     "state": 'Shutdown',
#     "VNC": False

# }]

@app.route("/")
def index():
    return render_template("index.html")

class api_socketio(Namespace):
    def on_connect(self):
        print("Client connected to test namespace\n\n")
    def on_test(self):
        print("test")
        emit("test")
    def on_get_cpu_overall_usage(self):
        print("cpu_overall_usage")
        cpu_overall = psutil.cpu_percent()
        emit("cpu_overall_usage", cpu_overall)
    def on_get_mem_usage(self):
        print("mem_usage")
        emit("mem_usage", psutil.virtual_memory().percent)
    def on_get_vm_results(self):
        print("vm_results")
        emit("vm_results", getvmresults())   
socketio.on_namespace(api_socketio('/api'))

class api_vm_manager(Resource):
    def post(self, action):
        if action == "create":
            name = request.form['name']
            os = request.form['os']
            machine_type = request.form['machine_type']
            bios_type = request.form['bios_type']
            min_mem = request.form['memory_min']
            mim_mem_unit = request.form['memory_min_unit']
            max_mem = request.form['memory_max']
            max_mem_unit = request.form['memory_max_unit']
            disk = False
            disk_size = request.form['disk_size']
            disk_size_unit = request.form['disk_size_unit']
            disk_type = request.form['disk_type']
            disk_bus = request.form['disk_bus']
            cdrom_pool = request.form['cdrom_pool']
            cdrom_path = request.form['cdrom_path']
            network = False
            network_source = request.form['network_source']
            network_model = request.form['network_model']

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
            print("network: " + str(network))
            print("network_source: " + network_source)
            print("network_model: " + network_model)

            vm = create_vm(name=name, machine_type=machine_type, bios_type=bios_type, mem_min=min_mem, mem_min_unit=mim_mem_unit, mem_max=max_mem, mem_max_unit=max_mem_unit, disk=disk, disk_size=disk_size, disk_size_unit=disk_size_unit, disk_type=disk_type, disk_bus=disk_bus, network=network, network_source=network_source, network_model=network_model)
            # vm.create()
            return '', 204
        else: 
            return 'Action not found', 404
api.add_resource(api_vm_manager, '/api/vm-manager/<string:action>')            

class api_vm_manager_action(Resource):
    def post(self, vmuuid, action):
        if action == "start":
            for vm in fakevm_results:
                if vm['uuid'] == vmuuid:
                    vm['state'] = 'Running'
                    return '', 204
        elif action == "stop":
            for vm in fakevm_results:
                if vm['uuid'] == vmuuid:
                    vm['state'] = 'Shutdown'
                    return '', 204
        elif action == "forcestop":
            for vm in fakevm_results:
                if vm['uuid'] == vmuuid:
                    vm['state'] = 'Shutdown'
                    return '', 204
        else:
            return 'Action not found', 404           
api.add_resource(api_vm_manager_action, '/api/vm-manager/<string:vmuuid>/<string:action>')      


class api_host_power(Resource):
    def post(self, powermsg):
        if powermsg == "shutdown":
            shutdown_result = subprocess.run(["shutdown", "-h", "now"], capture_output=True, text=True)
            if shutdown_result.returncode == 0:
                return '', 204
            else:
                return shutdown_result.stdout, 500
        elif powermsg == "reboot":
            reboot_result = subprocess.run(["reboot"], capture_output=True, text=True)
            if reboot_result.returncode == 0:
                return '', 204
            else:
                return reboot_result.stdout, 500
api.add_resource(api_host_power, '/api/host/power/<string:powermsg>')

if __name__ == '__main__':
    conn = libvirt.open('qemu:///system')
    app.run(debug=True, host="0.0.0.0")
