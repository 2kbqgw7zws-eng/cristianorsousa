from django.contrib import admin
from django.urls import path
from django.views.generic import RedirectView
# ATENÇÃO AQUI: Precisamos importar o 'download_relatorio_pdf' também
from imoveis.views import relatorio_geral, download_relatorio_pdf 

urlpatterns = [
    path('admin/', admin.site.urls),
    path('relatorio/', relatorio_geral, name='relatorio_geral'),
    
    # ESSA É A LINHA QUE ESTÁ FALTANDO NO SERVIDOR:
    path('relatorio/pdf/', download_relatorio_pdf, name='relatorio_pdf'),
    
    path('', RedirectView.as_view(url='/admin/')), 
]