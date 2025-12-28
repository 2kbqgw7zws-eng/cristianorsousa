from django.contrib import admin
from django.urls import path
from django.views.generic import RedirectView # <--- Importação nova
from imoveis.views import relatorio_geral

urlpatterns = [
    path('admin/', admin.site.urls),
    path('relatorio/', relatorio_geral, name='relatorio_geral'),
    # Essa linha abaixo redireciona a home vazia para o /admin automaticamente
    path('', RedirectView.as_view(url='/admin/')), 
]