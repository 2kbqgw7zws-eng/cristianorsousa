from django.contrib import admin
from django.shortcuts import redirect
from .models import DespesaAdvocacia, FaturamentoAdvocacia, RelatorioAdvocacia, ProcessoFaturamento

# Configuração para adicionar processos dentro do faturamento
class ProcessoInline(admin.TabularInline):
    model = ProcessoFaturamento
    extra = 1  # Quantidade de campos vazios que aparecem por padrão

@admin.register(FaturamentoAdvocacia)
class FaturamentoAdmin(admin.ModelAdmin):
    list_display = ('data', 'cliente', 'valor')
    inlines = [ProcessoInline] # Ativa a inserção de múltiplos processos

@admin.register(DespesaAdvocacia)
class DespesaAdmin(admin.ModelAdmin):
    list_display = ('data', 'descricao', 'valor')

@admin.register(RelatorioAdvocacia)
class RelatorioAdmin(admin.ModelAdmin):
    def changelist_view(self, request, extra_context=None):
        return redirect('relatorio_advocacia')
    
    def has_add_permission(self, request): return False
    def has_delete_permission(self, request, obj=None): return False