from django.contrib import admin # <--- ESSA LINHA É O QUE ESTÁ FALTANDO
from django.shortcuts import redirect
from .models import Imovel, Locacao, Despesa, RelatorioGeral

@admin.register(Imovel)
class ImovelAdmin(admin.ModelAdmin):
    list_display = ('nome',)

@admin.register(Locacao)
class LocacaoAdmin(admin.ModelAdmin):
    list_display = ('imovel', 'cliente', 'data_entrada', 'data_saida')

@admin.register(Despesa)
class DespesaAdmin(admin.ModelAdmin):
    list_display = ('imovel', 'categoria', 'data_pagamento', 'valor')

@admin.register(RelatorioGeral)
class RelatorioGeralAdmin(admin.ModelAdmin):
    def changelist_view(self, request, extra_context=None):
        return redirect('/relatorio/')

    def has_add_permission(self, request): return False
    def has_delete_permission(self, request, obj=None): return False