from django.contrib import admin
from django.shortcuts import redirect
from .models import Imovel, Locacao, Despesa, RelatorioGeral

@admin.register(Imovel)
class ImovelAdmin(admin.ModelAdmin):
    list_display = ('nome', 'valor_diaria', 'valor_compra', 'status')
    list_editable = ('status',) # Permite mudar o status rápido na lista

@admin.register(Locacao)
class LocacaoAdmin(admin.ModelAdmin):
    # 1. Adicionamos CPF e Telefone na listagem principal
    list_display = ('imovel', 'cliente', 'cpf', 'telefone', 'data_entrada', 'data_saida')
    
    # 2. Adicionamos uma barra de pesquisa (busca por nome ou CPF)
    search_fields = ('cliente', 'cpf')
    
    # 3. Adicionamos os filtros laterais
    list_filter = ('imovel', 'data_entrada')

    # 4. Criamos as opções de clique no menu "Ação"
    actions = ['gerar_relatorio_pdf', 'gerar_relatorio_excel']

    def gerar_relatorio_pdf(self, request, queryset):
        return redirect('/relatorio/pdf/')
    gerar_relatorio_pdf.short_description = "📄 Gerar PDF (Ano Completo)"

    def gerar_relatorio_excel(self, request, queryset):
        return redirect('/relatorio/excel/')
    gerar_relatorio_excel.short_description = "📊 Gerar Excel (Ano Completo)"

@admin.register(Despesa)
class DespesaAdmin(admin.ModelAdmin):
    list_display = ('imovel', 'categoria', 'descricao', 'data_pagamento', 'valor')
    list_filter = ('imovel', 'categoria')

@admin.register(RelatorioGeral)
class RelatorioGeralAdmin(admin.ModelAdmin):
    def changelist_view(self, request, extra_context=None):
        return redirect('/relatorio/')

    def has_add_permission(self, request): return False
    def has_delete_permission(self, request, obj=None): return False