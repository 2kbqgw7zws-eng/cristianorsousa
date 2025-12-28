from django.contrib import admin
from django.shortcuts import redirect
from .models import Imovel, Locacao, Despesa, RelatorioGeral

@admin.register(Imovel)
class ImovelAdmin(admin.ModelAdmin):
    list_display = ('nome', 'valor_diaria', 'valor_compra', 'status')
    list_editable = ('status',) 

@admin.register(Locacao)
class LocacaoAdmin(admin.ModelAdmin):
    list_display = ('imovel', 'cliente', 'cpf', 'telefone', 'data_entrada', 'data_saida')
    search_fields = ('cliente', 'cpf')
    list_filter = ('imovel', 'data_entrada')
    actions = ['gerar_relatorio_pdf', 'gerar_relatorio_excel']

    def gerar_relatorio_pdf(self, request, queryset):
        return redirect('/relatorio/pdf/')
    gerar_relatorio_pdf.short_description = "Gerar PDF"

    def gerar_relatorio_excel(self, request, queryset):
        return redirect('/relatorio/excel/')
    gerar_relatorio_excel.short_description = "Gerar Excel"

@admin.register(Despesa)
class DespesaAdmin(admin.ModelAdmin):
    # Colunas visíveis conforme sua imagem de despesas
    list_display = ('imovel', 'categoria', 'descricao', 'data_pagamento', 'valor')
    list_filter = ('imovel', 'categoria')
    search_fields = ('descricao',)
    
    # NOVAS AÇÕES ADICIONADAS AQUI:
    actions = ['gerar_despesas_pdf', 'gerar_despesas_excel']

    def gerar_despesas_pdf(self, request, queryset):
        return redirect('/relatorio/despesas/pdf/')
    gerar_despesas_pdf.short_description = "Gerar PDF"

    def gerar_despesas_excel(self, request, queryset):
        return redirect('/relatorio/despesas/excel/')
    gerar_despesas_excel.short_description = "Gerar Excel"

@admin.register(RelatorioGeral)
class RelatorioGeralAdmin(admin.ModelAdmin):
    def changelist_view(self, request, extra_context=None):
        return redirect('/relatorio/')

    def has_add_permission(self, request): return False
    def has_delete_permission(self, request, obj=None): return False