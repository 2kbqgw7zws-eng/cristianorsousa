from django.apps import AppConfig

class AdvocaciaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'advocacia'
    verbose_name = 'Advocacia' # Garante que o nome comece com 'A', mas o Django costuma colocar Auth no topo por padrão