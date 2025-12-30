from django.apps import AppConfig


class BatchesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.batches'
    
    def ready(self):
        import apps.batches.signals
