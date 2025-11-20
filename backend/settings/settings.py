import os
from .settingsException import SettingsException
import json
from sqlmodel import Field, SQLModel, select
from db import get_session

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

class SettingModel(SQLModel, table=True):
    __tablename__ = "settings"
    name: str = Field(primary_key=True)
    value: str = Field(nullable=False)
    description: str = Field(nullable=False)
    regexrules: str = Field(nullable=False)
    verifyDir: bool = Field(default=False)
    verifyFile: bool = Field(default=False)
    hidden: bool = Field(default=False)

class Setting:
    def __init__(self, name, value, description, regexrules=[], verifyDir=False, verifyFile=False, hidden=False):
        self.name = name
        self.value = value
        self.description = description
        self.regexrules = regexrules
        self.verifyFile = verifyFile
        self.verifyDir = verifyDir
        self.hidden = hidden
    
    @property
    def json(self):
        return { 
            'name': self.name,
            'value': self.value,
            'description': self.description,
            'regexrules': json.dumps([rule.json for rule in self.regexrules]),
            'verifyFile': self.verifyFile,
            'verifyDir': self.verifyDir,
            'hidden': self.hidden
        }
    
    @classmethod
    def from_model(cls, model: SettingModel):
        regexrules = json.loads(model.regexrules)
        return cls(
            name=model.name,
            value=model.value,
            description=model.description,
            regexrules=[RegexRule.from_json(rule) for rule in regexrules],
            verifyFile=model.verifyFile,
            verifyDir=model.verifyDir,
            hidden=model.hidden
        )
    
    def to_model(self) -> SettingModel:
        return SettingModel(
            name=self.name,
            value=self.value,
            description=self.description,
            regexrules=json.dumps([rule.json for rule in self.regexrules]),
            verifyFile=self.verifyFile,
            verifyDir=self.verifyDir,
            hidden=self.hidden
        )

class OvmfPathModel(SQLModel, table=True):
    __tablename__ = "settings_ovmfpaths"
    name: str = Field(primary_key=True)
    path: str = Field(nullable=False)
    description: str = Field(default="")

class OvmfPath:
    def __init__(self, name, path, description=""):
        self.name = name
        self.path = path
        self.description = description
    
    @property
    def json(self):
        return {
            'name': self.name,
            'path': self.path,
            'description': self.description
        }
    
    @classmethod
    def from_model(cls, model: OvmfPathModel):
        return cls(
            name=model.name,
            path=model.path,
            description=model.description
        )
    
    def to_model(self) -> OvmfPathModel:
        return OvmfPathModel(
            name=self.name,
            path=self.path,
            description=self.description
        )
    
class SettingsManager:
    def __init__(self):
        pass

    def create_ovmf_path(self, ovmf_path: OvmfPath):
        if self.verify_file(ovmf_path.path) == False:
            raise SettingsException(f"Path {ovmf_path.path} does not exist")
        if " " in ovmf_path.name:
            raise SettingsException("OVMF path name can not have spaces")
        
        with get_session() as session:
            # Check if it already exists
            existing = session.exec(
                select(OvmfPathModel).where(OvmfPathModel.name == ovmf_path.name)
            ).first()
            if existing:
                raise SettingsException(f"OVMF path with name '{ovmf_path.name}' already exists")
            
            model = ovmf_path.to_model()
            session.add(model)
            session.commit()

    def get_ovmf_path(self, name):
        with get_session() as session:
            model = session.exec(
                select(OvmfPathModel).where(OvmfPathModel.name == name)
            ).first()
            if model:
                return OvmfPath.from_model(model)
            else:
                raise SettingsException(f"OVMF path {name} does not exist")
        
    def get_ovmf_paths(self):
        with get_session() as session:
            models = session.exec(select(OvmfPathModel)).all()
            return [OvmfPath.from_model(model) for model in models]
    
    def update_ovmf_path(self, ovmf_path: OvmfPath):
        with get_session() as session:
            model = session.exec(
                select(OvmfPathModel).where(OvmfPathModel.name == ovmf_path.name)
            ).first()
            if not model:
                raise SettingsException(f"OVMF path {ovmf_path.name} does not exist")
            
            model.path = ovmf_path.path
            session.add(model)
            session.commit()

    def delete_ovmf_path(self, name):
        with get_session() as session:
            model = session.exec(
                select(OvmfPathModel).where(OvmfPathModel.name == name)
            ).first()
            if model:
                session.delete(model)
                session.commit()
    
    def create_setting(self, setting: Setting):
        if setting.verifyDir and self.verify_dir(setting.value) == False:
            raise SettingsException(f"Path {setting.value} does not exist")
        elif setting.verifyFile and self.verify_file(setting.value) == False:
            raise SettingsException(f"Path {setting.value} does not exist")
        if " " in setting.name:
            raise SettingsException("Setting name can not have spaces")
        
        with get_session() as session:
            # Check if it already exists
            existing = session.exec(
                select(SettingModel).where(SettingModel.name == setting.name)
            ).first()
            if existing:
                raise SettingsException(f"Setting with name '{setting.name}' already exists")
            
            model = setting.to_model()
            session.add(model)
            session.commit()

    def get_setting(self, name):
        with get_session() as session:
            model = session.exec(
                select(SettingModel).where(SettingModel.name == name)
            ).first()
            if model:
                return Setting.from_model(model)
            else:
                raise SettingsException(f"Setting {name} does not exist")
        
    def get_settings(self):
        with get_session() as session:
            models = session.exec(select(SettingModel)).all()
            return [Setting.from_model(model) for model in models]
    
    def update_setting(self, setting: Setting):
        with get_session() as session:
            model = session.exec(
                select(SettingModel).where(SettingModel.name == setting.name)
            ).first()
            if not model:
                raise SettingsException(f"Setting {setting.name} does not exist")
            
            model.value = setting.value
            model.description = setting.description
            model.regexrules = json.dumps([rule.json for rule in setting.regexrules])
            model.verifyDir = setting.verifyDir
            model.verifyFile = setting.verifyFile
            session.add(model)
            session.commit()

    def delete_setting(self, name):
        with get_session() as session:
            model = session.exec(
                select(SettingModel).where(SettingModel.name == name)
            ).first()
            if model:
                session.delete(model)
                session.commit()
    
    def verify_file(self, path):
        return os.path.isfile(path)
    
    def verify_dir(self, path):
        return os.path.isdir(path)
