from notifications import NotificationManager, NotificationType

notification_manager = NotificationManager()
notification_manager.create_notification(
    type=NotificationType.PROGRESS, 
    title='Progress Indeterminate', 
    message='Progress message', 
    progress=-1)

notification_manager.create_notification(
    type=NotificationType.PROGRESS, 
    title='Progress Determinate', 
    message='Progress message', 
    progress=50)

notification_manager.create_notification(
    type=NotificationType.INFO, 
    title='Info', 
    message='Info message')


print(notification_manager.get_notifications())
