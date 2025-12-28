from django.contrib import admin
from django.urls import path
from django.views.generic import RedirectView
# IMPORTANTE: Adicionei download_relatorio_excel aqui
from imoveis.views import relatorio_geral, download_relatorio_pdf, download_relatorio_excel 

urlpatterns = [
    path('admin/', admin.site.urls),
    path('relatorio/', relatorio_geral, name='relatorio_geral'),
    path('relatorio/pdf/', download_relatorio_pdf, name='relatorio_pdf'),
    # NOVA ROTA EXCEL:
    path('relatorio/excel/', download_relatorio_excel, name='relatorio_excel'),
    
    path('', RedirectView.as_view(url='/admin/')), 
]