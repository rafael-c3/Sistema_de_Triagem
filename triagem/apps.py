from django.apps import AppConfig

class TriagemConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'triagem'

    def ready(self):
        import triagem.signals # Importa nossos sinais quando o app estiver pronto