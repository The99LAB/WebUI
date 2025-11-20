from enum import Enum
from datetime import datetime
from sqlmodel import Field, SQLModel, select
from db import get_session
from typing import Optional

class NotificationType(Enum):
    ERROR = 'error'
    WARNING = 'warning'
    SUCCESS = 'success'
    INFO = 'info'
    PROGRESS = 'progress' # Progress: value from 0 to 100 or -1 for indeterminate

class NotificationModel(SQLModel, table=True):
    __tablename__ = "notifications"
    id: Optional[int] = Field(default=None, primary_key=True)
    type: str = Field(nullable=False)
    timestamp: str = Field(nullable=False)
    title: str = Field(nullable=False)
    message: str = Field(nullable=False)
    progress: int = Field(default=-1)

class Notification:
    def __init__(self, type:NotificationType, title, message, id=None, timestamp=None, progress=-1):
        self.id = id
        self.type = type
        self.timestamp = timestamp
        if timestamp is None:
            self.timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.title = title
        self.message = message
        self.progress = progress
    
    @property
    def json(self):
        return {
            'id': self.id,
            'type': self.type.value,
            'timestamp': self.timestamp,
            'title': self.title,
            'message': self.message,
            'progress': self.progress
        }
    
    @classmethod
    def from_json(cls, data):
        return cls(
            id=data['id'],
            type=NotificationType(data['type']),
            timestamp=data['timestamp'],
            title=data['title'],
            message=data['message'],
            progress=data['progress']
        )
    
    @classmethod
    def from_model(cls, model: NotificationModel):
        return cls(
            id=model.id,
            type=NotificationType(model.type),
            timestamp=model.timestamp,
            title=model.title,
            message=model.message,
            progress=model.progress
        )
    
    def to_model(self) -> NotificationModel:
        return NotificationModel(
            id=self.id,
            type=self.type.value,
            timestamp=self.timestamp,
            title=self.title,
            message=self.message,
            progress=self.progress
        )


class NotificationManager:
    def __init__(self):
        self.datetime_format = '%Y-%m-%d %H:%M:%S'
        
    def create_notification(self, notification:Notification):
        with get_session() as session:
            model = notification.to_model()
            session.add(model)
            session.commit()
            session.refresh(model)
            # Return the id of the notification
            return model.id
    
    def update_notification(self, notification:Notification):
        with get_session() as session:
            model = session.exec(
                select(NotificationModel).where(NotificationModel.id == notification.id)
            ).first()
            if not model:
                return
            
            model.type = notification.type.value
            model.timestamp = notification.timestamp
            model.title = notification.title
            model.message = notification.message
            model.progress = notification.progress
            session.add(model)
            session.commit()
    
    def get_notifications(self):
        with get_session() as session:
            models = session.exec(
                select(NotificationModel).order_by(NotificationModel.timestamp.desc())
            ).all()
            return [Notification.from_model(model) for model in models]
    
    def get_notification(self, notification_id):
        with get_session() as session:
            model = session.exec(
                select(NotificationModel).where(NotificationModel.id == notification_id)
            ).first()
            if model is None:
                return None
            return Notification.from_model(model)
    
    def delete_notification(self, notification:Notification):
        with get_session() as session:
            model = session.exec(
                select(NotificationModel).where(NotificationModel.id == notification.id)
            ).first()
            if model:
                session.delete(model)
                session.commit()
    
    def delete_all_notifications(self):
        with get_session() as session:
            # Delete all notifications except the ones with type progress which are not completed (progress != 100)
            non_progress = session.exec(
                select(NotificationModel).where(NotificationModel.type != NotificationType.PROGRESS.value)
            ).all()
            for notification in non_progress:
                session.delete(notification)
            
            completed_progress = session.exec(
                select(NotificationModel).where(
                    NotificationModel.type == NotificationType.PROGRESS.value,
                    NotificationModel.progress == 100
                )
            ).all()
            for notification in completed_progress:
                session.delete(notification)
            
            session.commit()

