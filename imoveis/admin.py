from django.contrib import admin
from django.shortcuts import redirect
from .models import Imovel, Locacao, Despesa, RelatorioGeral

@admin.register(Imovel)
class ImovelAdmin(admin.ModelAdmin):
    # Mostra colunas: Nome, Valor Diária, Valor Compra e Status
    list_display = ('nome', 'get_valor_diaria', 'get_valor_compra', 'status')
    list_editable = ('status',) 

    def get_valor_diaria(self, obj):
        if obj.valor_diaria:
            return f"R$ {obj.valor_diaria:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        return "R$ 0,00"
    get_valor_diaria.short_description = "Diária Padrão"

    def get_valor_compra(self, obj):
        if obj.valor_compra:
            return f"R$ {obj.valor_compra:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        return "R$ 0,00"
    get_valor_compra.short_description = "Investimento"

@admin.register(Locacao)
class LocacaoAdmin(admin.ModelAdmin):
    # AQUI ESTÁ A ORDEM DAS COLUNAS: Imovel, Cliente, CPF, Telefone, Entrada, Saída e VALOR
    list_display = ('imovel', 'cliente', 'cpf', 'telefone', 'data_entrada', 'data_saida', 'get_valor_cobrado')
    search_fields = ('cliente', 'cpf')
    list_filter = ('imovel', 'data_entrada')
    actions = ['gerar_relatorio_pdf', 'gerar_relatorio_excel']

    # Função que formata o valor para aparecer na lista
    def get_valor_cobrado(self, obj):
        if obj.valor_cobrado_diaria:
            return f"R$ {obj.valor_cobrado_diaria:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        return "R$ 0,00"
    get_valor_cobrado.short_description = "Valor Diária"

    def gerar_relatorio_pdf(self, request, queryset):
        return redirect('/relatorio/pdf/')
    gerar_relatorio_pdf.short_description = "Gerar PDF"

    def gerar_relatorio_excel(self, request, queryset):
        return redirect('/relatorio/excel/')
    gerar_relatorio_excel.short_description = "Gerar Excel"

@admin.register(Despesa)
class DespesaAdmin(admin.ModelAdmin):
    list_display = ('imovel', 'categoria', 'descricao', 'data_pagamento', 'get_valor')
    list_filter = ('imovel', 'categoria')
    search_fields = ('descricao',)
    actions = ['gerar_despesas_pdf', 'gerar_despesas_excel']

    def get_valor(self, obj):
        if obj.valor:
            return f"R$ {obj.valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        return "R$ 0,00"
    get_valor.short_description = "Valor"

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