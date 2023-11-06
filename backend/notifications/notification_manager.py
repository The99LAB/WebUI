import sqlite3
import os
from enum import Enum
from datetime import datetime

class NotificationType(Enum):
    ERROR = 'error'
    WARNING = 'warning'
    SUCCESS = 'success'
    INFO = 'info'
    PROGRESS = 'progress' # Progress: value from 0 to 100 or -1 for indeterminate

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

class NotificationManager:
    def __init__(self):
        self.conn = self._initialize_database()
        self.datetime_format = '%Y-%m-%d %H:%M:%S'
    
    def _initialize_database(self):
        database_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database.db')
        conn = sqlite3.connect(database_path)

        # Set row_factory to return a dictionary
        conn.row_factory = sqlite3.Row

        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY,
                type TEXT,
                timestamp TEXT,
                title TEXT,
                message TEXT,
                progress INTEGER
            )
        ''')
        conn.commit()
        return conn
        
    def create_notification(self, notification:Notification):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO notifications (type, timestamp, title, message, progress)
            VALUES (?, ?, ?, ?, ?)
        ''', (notification.type.value, notification.timestamp, notification.title, notification.message, notification.progress))
        self.conn.commit()
        # Return the id of the notification
        return cursor.lastrowid
    
    def update_notification(self, notification:Notification):
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE notifications
            SET type = ?,
                timestamp = ?,
                title = ?,
                message = ?,
                progress = ?
            WHERE id = ?
        ''', (notification.type.value, notification.timestamp, notification.title, notification.message, notification.progress, notification.id))
        self.conn.commit()
    
    def get_notifications(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM notifications')
        notifications = []
        for row in cursor.fetchall():
            notifications.append(Notification.from_json(row))
        return notifications
    
    def get_notification(self, notification_id):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM notifications WHERE id = ?', (notification_id,))
        row = cursor.fetchone()
        if row is None:
            return None
        return Notification.from_json(row)
    
    def delete_notification(self, notification:Notification):
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM notifications WHERE id = ?', (notification.id,))
        self.conn.commit()
    
    def delete_all_notifications(self):
        cursor = self.conn.cursor()
        # Delete all notifications except the ones with type progress which are completed (progress != 100)
        cursor.execute('DELETE FROM notifications WHERE type != ?', (NotificationType.PROGRESS.value,))
        cursor.execute('DELETE FROM notifications WHERE type = ? AND progress == ?', (NotificationType.PROGRESS.value, 100))
        self.conn.commit()
