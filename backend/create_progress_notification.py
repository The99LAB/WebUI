from notifications import NotificationManager, NotificationType, Notification

notification_manager = NotificationManager()

new_notification = Notification(NotificationType.PROGRESS, 'Progress', 'This is a progress notification', progress=0)
notification_manager.create_notification(new_notification)


for notification in notification_manager.get_notifications():
    print(notification.type)
