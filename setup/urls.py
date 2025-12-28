from django.contrib import admin
from django.urls import path
from imoveis import views # Certifique-se que o import aponta para sua pasta de views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('relatorio/', views.relatorio_geral, name='relatorio_geral'),
    path('relatorio/pdf/', views.download_relatorio_pdf, name='relatorio_pdf'),
    path('relatorio/excel/', views.download_relatorio_excel, name='relatorio_excel'),
    
    # ADICIONE ESTAS DUAS LINHAS ABAIXO:
    path('relatorio/despesas/pdf/', views.download_despesas_pdf, name='download_despesas_pdf'),
    path('relatorio/despesas/excel/', views.download_despesas_excel, name='download_despesas_excel'),
]