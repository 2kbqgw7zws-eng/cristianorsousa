from django.contrib import admin
from .models import DespesaAdvocacia, FaturamentoAdvocacia, RelatorioAdvocacia

@admin.register(DespesaAdvocacia)
class DespesaAdmin(admin.ModelAdmin):
    list_display = ('data', 'descricao', 'valor')

@admin.register(FaturamentoAdvocacia)
class FaturamentoAdmin(admin.ModelAdmin):
    list_display = ('data', 'cliente', 'valor')

@admin.register(RelatorioAdvocacia)
class RelatorioAdmin(admin.ModelAdmin):
    
    def has_add_permission(self, request): return False
    def has_delete_permission(self, request, obj=None): return False