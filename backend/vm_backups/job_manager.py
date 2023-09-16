from .exceptions import jobManagerException
import sqlite3
import json
from enum import Enum
from cron_validator import CronValidator
from .job_actions import Backup, Restore
import os

class Schedule:
    def __init__(self, cron_expression=None):
        self.cron_expression = cron_expression
        self.validate_cron_expression()
    
    def validate_cron_expression(self):
        if self.cron_expression is None:
            return
        try:
            CronValidator.parse(self.cron_expression)
        except ValueError as e:
            raise jobManagerException(f'Invalid cron expression: {e}')


class VirtualMachine:
    def __init__(self, uuid:str, disks:list=[]):
        self.uuid = uuid
        self.disks = disks

    @property
    def json(self):
        return {
            'uuid': self.uuid,
            'disks': self.disks
        }
    
    @classmethod
    def from_json(cls, data):
        return cls(
            uuid=data['uuid'],
            disks=data['disks']
        )


class RetentionPolicyType(Enum):
    KEEP_ALL = 'keep_all'
    KEEP_LAST = 'keep_last'


class RetentionPolicy:
    def __init__(self, policy_type:RetentionPolicyType, value=None):
        self.value = value
        if not isinstance(self.value, int) and self.value is not None:
            raise jobManagerException('Invalid retention policy value')
        self.policy_type = policy_type.value
    
    @property
    def json(self):
        return {
            'policy_type': self.policy_type,
            'value': self.value
        }
    
    @classmethod
    def from_json(cls, data):
        return cls(
            policy_type=RetentionPolicyType(data['policy_type']),
            value=data['value']
        )


class BackupJob:
    def __init__(self, name:str, storage:str, schedule:Schedule, retention_policy:RetentionPolicy, enabled=True, vms:list=[], id=None,):
        self.id = id
        self.enabled = enabled
        self.name = name
        self.storage = storage
        self.schedule = schedule
        self.vms = vms
        self.retention_policy = retention_policy
        for index, vm in enumerate(self.vms):
            if not isinstance(vm, VirtualMachine):
                raise jobManagerException(f'Invalid virtual machine: {index}')
    
    def add_vm(self, vm):
        if not isinstance(vm, VirtualMachine):
            raise jobManagerException('Invalid virtual machine')
        self.vms.append(vm)
    
    def remove_vm(self, vm):
        if not isinstance(vm, VirtualMachine):
            raise jobManagerException('Invalid virtual machine')
        self.vms.remove(vm)

    @property
    def json(self):
        return {
            'enabled': self.enabled,
            'name': self.name,
            'storage': self.storage,
            'schedule': self.schedule.cron_expression,
            'vms': [vm.json for vm in self.vms],
            'retention_policy': self.retention_policy.json
        }
    
    @classmethod
    def from_json(cls, data):
        return cls(
            id=data['id'],
            enabled=data['enabled'],
            name=data['name'],
            storage=data['storage'],
            schedule=Schedule(data['schedule']),
            vms=[VirtualMachine.from_json(vm) for vm in data['vms']],
            retention_policy=RetentionPolicy.from_json(data['retention_policy'])
        )

class BackupJobManager:
    def __init__(self):
        # self.db_path = "/var/lib/LibvirtKVMBackup/database.db"
        self.conn = self._initialize_database()

    def _initialize_database(self):
        # if not os.path.exists(os.path.dirname(self.db_path)):
        #     os.makedirs(os.path.dirname(self.db_path))

        # Create database connection
        database_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database.db')
        conn = sqlite3.connect(database_path, detect_types=sqlite3.PARSE_DECLTYPES)

        # Set row_factory to return a dictionary
        conn.row_factory = sqlite3.Row

        # Register boolean adapter and converter
        sqlite3.register_adapter(bool, lambda b: int(b))
        sqlite3.register_converter("BOOLEAN", lambda v: bool(int(v)))

        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS backup_jobs (
                id INTEGER PRIMARY KEY,
                enabled BOOLEAN,
                name TEXT UNIQUE,
                schedule TEXT,
                storage TEXT,
                vms TEXT,
                retention_policy TEXT
            )
        ''')
        conn.commit()
        return conn

    def create_backup_job(self, backup_job:BackupJob):
        backup_job = backup_job.json
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO backup_jobs (
                enabled,
                name,
                schedule,
                storage,
                vms,
                retention_policy
            ) VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            backup_job['enabled'],
            backup_job['name'],
            backup_job['schedule'],
            backup_job['storage'],
            json.dumps(backup_job['vms']),
            json.dumps(backup_job['retention_policy'])
        ))
        self.conn.commit()

    def get_backup_job(self, job_name):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM backup_jobs WHERE name = ?', (job_name,))
        backup_job = cursor.fetchone()
        if backup_job is None:
            raise jobManagerException('Backup job not found')
        return BackupJob.from_json({
            'id': backup_job['id'],
            'enabled': backup_job['enabled'],
            'name': backup_job['name'],
            'schedule': backup_job['schedule'],
            'storage': backup_job['storage'],
            'vms': json.loads(backup_job['vms']),
            'retention_policy': json.loads(backup_job['retention_policy'])
        })
    
    def get_all_backup_jobs(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM backup_jobs')
        backup_jobs = cursor.fetchall()
        return [BackupJob.from_json({
            'id': backup_job['id'],
            'enabled': backup_job['enabled'],
            'name': backup_job['name'],
            'schedule': backup_job['schedule'],
            'storage': backup_job['storage'],
            'vms': json.loads(backup_job['vms']),
            'retention_policy': json.loads(backup_job['retention_policy'])
        }) for backup_job in backup_jobs]
    
    def start_backup_job(self, job_name):
        backup_job = self.get_backup_job(job_name)
        try:
            Backup(backup_job).start()
        except Exception as e:
            raise jobManagerException(f'Failed to start backup job: {e}')

    def restore_backup_job(self, job_name, timestamp):
        backup_job = self.get_backup_job(job_name)
        backup_job_json_path = os.path.join(backup_job.storage, timestamp, 'backup-job.json')
        if not os.path.exists(backup_job_json_path):
            raise jobManagerException('Backup job with given timestamp not found')
        try:
            Restore(backup_job_json_path).start()
        except Exception as e:
            raise jobManagerException(f'Failed to restore backup job: {e}')
        
    def list_job_timestamps(self, job_name):
        backup_job = self.get_backup_job(job_name)
        if not os.path.exists(backup_job.storage):
            raise jobManagerException('Backup job not found')
        return sorted(os.listdir(backup_job.storage), reverse=True)
    
    @classmethod
    def restore_from_json(path):
        if not os.path.exists(path):
            raise jobManagerException('Backup job json file not found')
        try:
            Restore(path).start()
        except Exception as e:
            raise jobManagerException(f'Failed to restore backup job: {e}')
    
    def delete_backup_job(self, job_name):
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM backup_jobs WHERE name = ?', (job_name,))
        self.conn.commit()