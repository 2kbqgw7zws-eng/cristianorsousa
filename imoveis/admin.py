from django.contrib import admin
from .models import Imovel, Locacao, Despesa, RelatorioGeral # Certifique-se de importar todos

@admin.register(Imovel)
class ImovelAdmin(admin.ModelAdmin):
    list_display = ('nome', 'valor_diaria', 'status')

@admin.register(Locacao)
class LocacaoAdmin(admin.ModelAdmin):
    list_display = ('imovel', 'cliente', 'data_entrada', 'data_saida')

@admin.register(Despesa)
class DespesaAdmin(admin.ModelAdmin):
    list_display = ('imovel', 'categoria', 'data_pagamento', 'valor')
    list_filter = ('imovel', 'categoria')

# ESTE BLOCO ABAIXO É O QUE CRIA O BOTÃO DO RELATÓRIO
@admin.register(RelatorioGeral)
class RelatorioGeralAdmin(admin.ModelAdmin):
    def has_add_permission(self, request): return False
    def has_delete_permission(self, request, obj=None): return False