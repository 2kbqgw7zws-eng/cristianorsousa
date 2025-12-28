from django.contrib import admin
from .models import Imovel, Locacao, Despesa # <--- Adicionei Despesa aqui

@admin.register(Imovel)
class ImovelAdmin(admin.ModelAdmin):
    list_display = ('nome',)

@admin.register(Locacao)
class LocacaoAdmin(admin.ModelAdmin):
    list_display = ('imovel', 'data_entrada', 'data_saida', 'valor_cobrado_diaria')
    list_filter = ('imovel', 'data_entrada')

@admin.register(Despesa) # <--- Novo registro
class DespesaAdmin(admin.ModelAdmin):
    list_display = ('imovel', 'categoria', 'data_pagamento', 'valor')
    list_filter = ('imovel', 'categoria', 'data_pagamento')
    search_fields = ('descricao',)