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

class NotificationTimeType(Enum):
    STRING = 'string'
    DATETIME = 'datetime'

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
        
    def create_notification(self, type:NotificationType, title, message, progress=None):
        if type == NotificationType.PROGRESS:
            if progress is None:
                raise Exception('Progress must be specified when creating a progress notification')
        else:
            progress = 0
        cursor = self.conn.cursor()
        timestamp = datetime.now().strftime(self.datetime_format)
        cursor.execute('''
            INSERT INTO notifications (type, timestamp, title, message, progress)
            VALUES (?, ?, ?, ?, ?)
        ''', (type.value, timestamp, title, message, progress))
        self.conn.commit()

        # Return the id of the notification
        return cursor.lastrowid
    
    def update_notification(self, notification_id, progress):
        cursor = self.conn.cursor()
        cursor.execute('UPDATE notifications SET progress = ? WHERE id = ?', (progress, notification_id))
        self.conn.commit()
    
    def get_notifications(self, time_type=NotificationTimeType.STRING):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM notifications')
        notifications = [dict(row) for row in cursor.fetchall()]

        if time_type == NotificationTimeType.DATETIME:
            for notification in notifications:
                notification['timestamp'] = datetime.strptime(notification['timestamp'], self.datetime_format)

        return notifications
    
    def delete_notification(self, notification_id):
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM notifications WHERE id = ?', (notification_id,))
        self.conn.commit()
    
    def delete_all_notifications(self):
        cursor = self.conn.cursor()
        # Delete all notifications except the ones with type progress which are completed (progress != 100)
        cursor.execute('DELETE FROM notifications WHERE type != ?', (NotificationType.PROGRESS.value,))
        cursor.execute('DELETE FROM notifications WHERE type = ? AND progress == ?', (NotificationType.PROGRESS.value, 100))
        self.conn.commit()
