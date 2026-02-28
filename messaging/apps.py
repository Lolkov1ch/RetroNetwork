from django.apps import AppConfig


class MessagingConfig(AppConfig):
    name = 'messaging'
    default_auto_field = 'django.db.models.BigAutoField'    
    def ready(self):
        import messaging.signals