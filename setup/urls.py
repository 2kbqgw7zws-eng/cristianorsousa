from django.contrib import admin
from django.urls import path
from imoveis import views as imoveis_views
from advocacia import views as advocacia_views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # --- ROTAS DE IMÓVEIS ---
    path('relatorio/', imoveis_views.relatorio_geral, name='relatorio_geral'),
    path('relatorio/pdf/', imoveis_views.download_relatorio_pdf, name='download_relatorio_pdf'),
    path('relatorio/excel/', imoveis_views.download_relatorio_excel, name='download_relatorio_excel'),
    path('despesas/pdf/', imoveis_views.download_despesas_pdf, name='download_despesas_pdf'),
    path('despesas/excel/', imoveis_views.download_despesas_excel, name='download_despesas_excel'),

    # --- ROTAS DE ADVOCACIA ---
    path('admin/advocacia/relatorio/', advocacia_views.relatorio_advocacia, name='relatorio_advocacia'),
    path('admin/advocacia/relatorio/pdf/', advocacia_views.download_advocacia_pdf, name='download_advocacia_pdf'),
    path('admin/advocacia/relatorio/excel/', advocacia_views.download_advocacia_excel, name='download_advocacia_excel'),
]