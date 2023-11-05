from notifications import NotificationManager, NotificationType

notification_manager = NotificationManager()

notifications = notification_manager.get_notifications()
for notification in notifications:
    if notification["type"] == 'progress':
        notification_manager.delete_notification(notification["id"])