from django.apps import AppConfig

class MyappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'myapp'

    def ready(self):
        # Esta linha é crucial: importa e conecta os nossos sinais
        # quando a aplicação está pronta.
        import myapp.signals
