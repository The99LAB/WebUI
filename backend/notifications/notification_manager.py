import sqlite3
import os
from enum import Enum
from datetime import datetime

class NotificationType(Enum):
    ERROR = 'error'
    WARNING = 'warning'
    SUCCESS = 'success'
    INFO = 'info'

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
                message TEXT
            )
        ''')
        conn.commit()
        return conn
        
    def create_notification(self, type:NotificationType, title, message):
        cursor = self.conn.cursor()
        timestamp = datetime.now().strftime(self.datetime_format)
        cursor.execute('''
            INSERT INTO notifications (type, timestamp, title, message)
            VALUES (?, ?, ?, ?)
        ''', (type.value, timestamp, title, message))
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
        cursor.execute('DELETE FROM notifications')
        self.conn.commit()
