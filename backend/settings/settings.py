import sqlite3
import os
from .settingsException import SettingsException
import json

class RegexRule:
    def __init__(self, regex, description):
        self.regex = regex
        self.description = description
    
    @property
    def json(self):
        return {
            'regex': self.regex,
            'description': self.description
        }
    
    @classmethod
    def from_json(cls, data):
        return cls(
            regex=data['regex'],
            description=data['description']
        )

class Setting:
    def __init__(self, name, value, description, regexrules=[], verifyDir=False, verifyFile=False):
        self.name = name
        self.value = value
        self.description = description
        self.regexrules = regexrules
        self.verifyFile = verifyFile
        self.verifyDir = verifyDir
    
    @property
    def json(self):
        return { 
            'name': self.name,
            'value': self.value,
            'description': self.description,
            'regexrules': json.dumps([rule.json for rule in self.regexrules]),
            'verifyFile': self.verifyFile,
            'verifyDir': self.verifyDir
        }
    
    @classmethod
    def from_json(cls, data):
        regexrules = json.loads(data['regexrules'])
        return cls(
            name=data['name'],
            value=data['value'],
            description=data['description'],
            regexrules=[RegexRule.from_json(rule) for rule in regexrules],
            verifyFile=data['verifyFile'],
            verifyDir=data['verifyDir']
        )
    
class OvmfPath:
    def __init__(self, name, path):
        self.name = name
        self.path = path
    
    @property
    def json(self):
        return {
            'name': self.name,
            'path': self.path
        }
    
    @classmethod
    def from_json(cls, data):
        return cls(
            name=data['name'],
            path=data['path']
        )
    
class SettingsManager:
    def __init__(self):
        self.conn = self._initialize_database()

    def _initialize_database(self):
        database_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database.db')
        conn = sqlite3.connect(database_path)

        # Set row_factory to return a dictionary
        conn.row_factory = sqlite3.Row

         # Register boolean adapter and converter
        sqlite3.register_adapter(bool, lambda b: int(b))
        sqlite3.register_converter("BOOLEAN", lambda v: bool(int(v)))

        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS "settings" (
                name TEXT PRIMARY KEY,
                value TEXT,
                description TEXT,
                regexrules TEXT,
                verifyDir BOOLEAN,
                verifyFile BOOLEAN
            )''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS "settings_ovmfpaths" (
                name TEXT PRIMARY KEY,
                path TEXT
            )''')
        conn.commit()
        return conn
    
    def create_ovmf_path(self, ovmf_path:OvmfPath):
        cursor = self.conn.cursor()
        if self.verify_file(ovmf_path.path) == False:
            raise SettingsException(f"Path {ovmf_path.path} does not exist")
        if " " in ovmf_path.name:
            raise SettingsException("OVMF path name can not have spaces")
        try:
            cursor.execute('''INSERT INTO settings_ovmfpaths (name, path) VALUES (?, ?)''', 
                        (ovmf_path.name, ovmf_path.path))
        except sqlite3.IntegrityError as e:
            raise SettingsException(e)
        self.conn.commit()

    def get_ovmf_path(self, name):
        cursor = self.conn.cursor()
        cursor.execute('''SELECT * FROM settings_ovmfpaths WHERE name=?''', (name,))
        row = cursor.fetchone()
        if row:
            return OvmfPath.from_json(row)
        else:
            raise SettingsException(f"OVMF path {name} does not exist")
        
    def get_ovmf_paths(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM settings_ovmfpaths')
        ovmf_paths = []
        for row in cursor.fetchall():
            ovmf_paths.append(OvmfPath.from_json(row))
        return ovmf_paths
    
    def update_ovmf_path(self, ovmf_path:OvmfPath):
        cursor = self.conn.cursor()
        cursor.execute('''UPDATE settings_ovmfpaths SET path=? WHERE name=?''', 
                       (ovmf_path.path, ovmf_path.name))
        self.conn.commit()

    def delete_ovmf_path(self, name):
        cursor = self.conn.cursor()
        cursor.execute('''DELETE FROM settings_ovmfpaths WHERE name=?''', (name,))
        self.conn.commit()
    
    def create_setting(self, setting:Setting):
        cursor = self.conn.cursor()
        if setting.verifyDir and self.verify_dir(setting.value) == False:
            raise SettingsException(f"Path {setting.value} does not exist")
        elif setting.verifyFile and self.verify_file(setting.value) == False:
            raise SettingsException(f"Path {setting.value} does not exist")
        if " " in setting.name:
            raise SettingsException("Setting name can not have spaces")
        try:
            cursor.execute('''INSERT INTO settings (name, value, description, regexrules, verifyDir, verifyFile) VALUES (?, ?, ?, ?, ?, ?)''', 
                           (setting.name, setting.value, setting.description, setting.json['regexrules'],  setting.verifyDir, setting.verifyFile))
        except sqlite3.IntegrityError as e:
            raise SettingsException(e)
        self.conn.commit()

    def get_setting(self, name):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM settings WHERE name=?
        ''', (name,))
        row = cursor.fetchone()
        if row:
            return Setting.from_json(row)
        else:
            raise SettingsException(f"Setting {name} does not exist")
        
    def get_settings(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM settings')
        settings = []
        for row in cursor.fetchall():
            settings.append(Setting.from_json(row))
        return settings
    
    def update_setting(self, setting:Setting):
        cursor = self.conn.cursor()
        try:
            cursor.execute('''UPDATE settings SET value=?, description=?, regexrules=?, verifyDir=?, verifyFile=? WHERE name=?''', 
                       (setting.value, setting.description, setting.json['regexrules'], setting.verifyDir, setting.verifyFile, setting.name))
        except sqlite3.IntegrityError as e:
            raise SettingsException(e)
        self.conn.commit()

    def delete_setting(self, name):
        cursor = self.conn.cursor()
        cursor.execute('''
            DELETE FROM settings WHERE name=?
        ''', (name,))
        self.conn.commit()
    
    def verify_file(self, path):
        return os.path.isfile(path)
    
    def verify_dir(self, path):
        return os.path.isdir(path)
