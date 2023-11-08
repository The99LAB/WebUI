import sqlite3
import os
from .settingsException import SettingsException

class Setting:
    def __init__(self, name, value, description, regex="", regex_description="", verifyPath=False):
        self.name = name
        self.value = value
        self.description = description
        self.regex = regex
        self.regex_description = regex_description
        self.verifyPath = verifyPath
    
    @property
    def json(self):
        return { 
            'name': self.name,
            'value': self.value,
            'description': self.description,
            'regex': self.regex,
            'regex_description': self.regex_description,
            'verifyPath': self.verifyPath
        }
    
    @classmethod
    def from_json(cls, data):
        return cls(
            name=data['name'],
            value=data['value'],
            description=data['description'],
            regex=data['regex'],
            regex_description=data['regex_description'],
            verifyPath=data['verifyPath']
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

        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                name TEXT PRIMARY KEY,
                value TEXT,
                description TEXT
                regex TEXT,
                regex_description TEXT,
                verifyPath BOOLEAN
            ),
            CREATE TABLE IF NOT EXISTS settings_ovmfpaths (
                name TEXT PRIMARY KEY,
                path TEXT
        ''')
        conn.commit()
        return conn
    
    def create_ovmf_path(self, ovmf_path:OvmfPath):
        cursor = self.conn.cursor()
        if self.verify_path(ovmf_path.path) == False:
            raise SettingsException(f"Path {ovmf_path.path} does not exist")
        if " " in ovmf_path.name:
            raise SettingsException("OVMF path name can not have spaces")
        cursor.execute('''INSERT INTO settings_ovmfpaths (name, path) VALUES (?, ?)''', 
                       (ovmf_path.name, ovmf_path.path))
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
        if setting.verifyPath and self.verify_path(setting.value) == False:
            raise SettingsException(f"Path {setting.value} does not exist")
        if " " in setting.name:
            raise SettingsException("Setting name can not have spaces")
        cursor.execute('''INSERT INTO settings (name, value, description, regex, regex_description, verifyPath) VALUES (?, ?, ?, ?, ?, ?)''', (setting.name, setting.value, setting.description, setting.regex, setting.regex_description, setting.verifyPath))
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
        cursor.execute('''UPDATE settings SET value=?, description=?, regex=?, regex_description=?, verifyPath=? WHERE name=?''', 
                       (setting.value, setting.description, setting.regex, setting.regex_description, setting.verifyPath, setting.name))
        self.conn.commit()

    def delete_setting(self, name):
        cursor = self.conn.cursor()
        cursor.execute('''
            DELETE FROM settings WHERE name=?
        ''', (name,))
        self.conn.commit()

    def verify_path(self, path):
        return os.path.exists(path) and os.path.isfile(path)
