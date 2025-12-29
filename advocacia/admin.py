from django.contrib import admin
from django.shortcuts import redirect
from .models import DespesaAdvocacia, FaturamentoAdvocacia, RelatorioAdvocacia, ProcessoFaturamento

class ProcessoInline(admin.TabularInline):
    model = ProcessoFaturamento
    extra = 1

@admin.register(FaturamentoAdvocacia)
class FaturamentoAdmin(admin.ModelAdmin):
    list_display = ('data', 'cliente', 'cpf_cnpj', 'valor')
    search_fields = ('cliente', 'cpf_cnpj')
    inlines = [ProcessoInline]

@admin.register(DespesaAdvocacia)
class DespesaAdmin(admin.ModelAdmin):
    list_display = ('data', 'descricao', 'local', 'valor')
    search_fields = ('descricao', 'local')

@admin.register(RelatorioAdvocacia)
class RelatorioAdmin(admin.ModelAdmin):
    def changelist_view(self, request, extra_context=None):
        return redirect('relatorio_advocacia')
    
    def has_add_permission(self, request): return False
    def has_delete_permission(self, request, obj=None): return False