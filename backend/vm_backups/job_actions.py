from datetime import datetime
import os
import logging
import libvirt
import json
import xml.etree.ElementTree as ET
import subprocess
import time
from .exceptions import restoreException, backupException

class BaseFunctionality:
    @staticmethod
    def virtual_machine_disks(xml):
        disks = []
        xml = ET.fromstring(xml)
        for disk in xml.findall('devices/disk'):
            if disk.get('device') == 'disk':
                disks.append({
                    'source': disk.find('source').get('file'),
                    'target': disk.find('target').get('dev')
                })
        return disks
    
    @staticmethod
    def virtual_machine_nvram(xml):
        xml = ET.fromstring(xml)
        xml_nvram = xml.find('os/nvram')
        if xml_nvram is not None:
            return xml_nvram.text
        return None

    @staticmethod
    def connect_to_libvirt():
        return libvirt.open('qemu:///system')
    
    @staticmethod
    def shutdown_domain(conn, uuid):
        domain = conn.lookupByUUIDString(uuid)
        domain.shutdown()

        # Wait for the domain to shutdown
        max_wait = 60
        while domain.isActive():
            max_wait -= 1
            time.sleep(1)
            if max_wait == 0:
                domain.destroy()
                break

class Backup:
    def __init__(self, backupjob):
        self.error = False
        self.backupjob = backupjob
        self.timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def create_directory(self):
        self.path = os.path.join(self.backupjob.storage, self.timestamp)
        os.makedirs(self.path)

    def create_log(self):
        self.log_path = os.path.join(self.path, 'backup-log.log')
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)
        logging.basicConfig(filename=self.log_path, level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')

    def write_backup_job(self):
        self.backupjobpath = os.path.join(self.path, 'backup-job.json')
        with open(self.backupjobpath, 'w') as f:
            # add 'name' to each vm
            backupjob = self.backupjob.json
            for vm in backupjob['vms']:
                vm['name'] = self.conn.lookupByUUIDString(vm['uuid']).name()
            f.write(json.dumps(backupjob, indent=4))

    def virtual_machine_disks(self, vm):
        xml = self.conn.lookupByUUIDString(vm.uuid).XMLDesc()
        return BaseFunctionality.virtual_machine_disks(xml)
    
    def raise_error(self, message):
        self.error = True
        logging.error(message)
    
    def start(self):
        self.create_directory()
        self.create_log()
        self.conn = BaseFunctionality.connect_to_libvirt()
        self.write_backup_job()
        for vm in self.backupjob.vms:
            vmname = self.conn.lookupByUUIDString(vm.uuid).name()
            vm_backup_path = os.path.join(self.path, vmname)
            os.makedirs(vm_backup_path)
            logging.info(f'Backing up virtual machine {vmname}')
            
            # backup the xml
            logging.info(f'VM: {vmname} - Backing up XML')
            xml = self.conn.lookupByUUIDString(vm.uuid).XMLDesc()
            with open(os.path.join(vm_backup_path, 'xml.xml'), 'w') as f:
                f.write(xml)
            logging.info(f'VM: {vmname} - XML backed up')

            # backup the disks
            for disk in self.virtual_machine_disks(vm):
                if disk['target'] not in vm.disks:
                    continue
                
                original_disk_path = disk['source']
                disk_file_name = os.path.basename(original_disk_path)
                disk_backup_path = os.path.join(vm_backup_path, disk_file_name)
                
                # copy the disk
                logging.info(f'VM: {vmname} - Backing up disk {disk_file_name}')
                try:
                    subprocess.check_output(['cp', '-a', original_disk_path, disk_backup_path])
                except subprocess.CalledProcessError as e:
                    self.raise_error(f'VM: {vmname} - Failed to backup disk {disk_file_name}')
                    continue
                logging.info(f'VM: {vmname} - Disk {disk_file_name} backed up')
            
            # backup the nvram
            logging.info(f'VM: {vmname} - Backing up NVRAM')
            nvram_path = BaseFunctionality.virtual_machine_nvram(xml)
            if nvram_path is not None:
                nvram_backup_path = os.path.join(vm_backup_path, 'nvram.fd')
                try:
                    subprocess.check_output(['cp', '-a', nvram_path, nvram_backup_path])
                    logging.info(f'VM: {vmname} - NVRAM backed up')
                except subprocess.CalledProcessError as e:
                    self.raise_error(f'VM: {vmname} - Failed to backup NVRAM')

            logging.info(f'Virtual machine {vmname} backed up')

        logging.info('All virtual machines backed up')
        if self.error:
            raise backupException('Failed to backup virtual machine')


class Restore:
    def __init__(self, backupjsonpath):
        with open(backupjsonpath, 'r') as f:
            self.backupjob = json.loads(f.read())
        self.error = False
        self.backup_job_path = os.path.dirname(backupjsonpath)
        self.timestamp = os.path.basename(self.backup_job_path)
        self.conn = BaseFunctionality.connect_to_libvirt()
        self.create_log()

    def create_log(self):
        self.log_path = os.path.join(self.backup_job_path, 'restore-log.log')
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)
        logging.basicConfig(filename=self.log_path, level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')

    def raise_error(self, message):
        self.error = True
        logging.error(message)

    def start(self):
        for vm in self.backupjob['vms']:
            vmname = vm['name']
            logging.info(f'Restoring virtual machine {vmname}')
            vm_backup_path = os.path.join(self.backup_job_path, vmname)
            
            # If the domain exists, shut it down
            domain_was_running = False
            try:
                domain = self.conn.lookupByName(vmname)
                logging.info(f'VM: {vmname} - Shutting down')
                BaseFunctionality.shutdown_domain(self.conn, domain.UUIDString())
                logging.info(f'VM: {vmname} - Shut down')
                domain_was_running = True
            except libvirt.libvirtError:
                logging.info(f'VM: {vmname} - Not running')
                pass
            
            # Read the xml
            logging.info(f'VM: {vmname} - Getting XML')
            vm_backup_xml_path = os.path.join(vm_backup_path, 'xml.xml')
            with open(vm_backup_xml_path, 'r') as f:
                xml = f.read()

            # restore the disks
            for disk in BaseFunctionality.virtual_machine_disks(xml):
                if disk['target'] not in vm['disks']:
                    continue
                
                logging.info(f'VM: {vmname} - Restoring disk {disk["source"]}')
                original_disk_path = disk['source']
                disk_file_name = os.path.basename(original_disk_path)
                disk_backup_path = os.path.join(vm_backup_path, disk_file_name)
                try:
                    subprocess.check_output(['cp', '-a', disk_backup_path, original_disk_path])
                    logging.info(f'VM: {vmname} - Disk {disk["source"]} restored')
                except subprocess.CalledProcessError as e:
                    self.raise_error(f'VM: {vmname} - Failed to restore disk {disk["source"]}')
            
            # restore the nvram
            vm_xml_nvram_path = BaseFunctionality.virtual_machine_nvram(xml)
            if vm_xml_nvram_path is not None:
                logging.info(f'VM: {vmname} - Restoring NVRAM')
                nvram_backup_path = os.path.join(vm_backup_path, 'nvram.fd')
                try:
                    subprocess.check_output(['cp', '-a', nvram_backup_path, vm_xml_nvram_path])
                    logging.info(f'VM: {vmname} - NVRAM restored')
                except subprocess.CalledProcessError as e:
                    self.raise_error(f'VM: {vmname} - Failed to restore NVRAM')

            # restore the xml
            self.conn.defineXML(xml)
            logging.info(f'VM: {vmname} - XML restored')

            # If the domain was running, start it
            if domain_was_running:
                logging.info(f'VM: {vmname} - Starting')
                domain = self.conn.lookupByName(vmname)
                domain.create()
                logging.info(f'VM: {vmname} - Started')

            logging.info(f'Virtual machine {vmname} restored')
        
        logging.info('All virtual machines restored')
        if self.error:
            raise restoreException('Failed to restore virtual machine')
