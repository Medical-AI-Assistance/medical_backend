from users_auth.models.models_notification import Notification

def create_notification(user, title, message, notification_type='SYSTEM'):
    """
    Utility function to create a notification for a user.
    """
    try:
        return Notification.objects.create(
            user=user,
            title=title,
            message=message,
            notification_type=notification_type
        )
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to create notification: {str(e)}")
        return None
