from django.contrib import admin
from django.shortcuts import redirect # Importante para o redirecionamento
from .models import Imovel, Locacao, RelatorioGeral

# Configuração do Imóvel
class ImovelAdmin(admin.ModelAdmin):
    list_display = ('nome', 'valor_diaria', 'status')
    list_editable = ('status',)

# Configuração da Locação
class LocacaoAdmin(admin.ModelAdmin):
    list_display = ('imovel', 'cliente', 'cpf', 'telefone', 'data_entrada', 'data_saida', 'valor_cobrado_diaria')
    list_filter = ('imovel', 'data_entrada')
    search_fields = ('cliente', 'cpf', 'telefone')

# Configuração do Botão de Relatório
class RelatorioGeralAdmin(admin.ModelAdmin):
    def changelist_view(self, request, extra_context=None):
        # Quando clicar no botão, redireciona para a URL do relatório
        return redirect('/relatorio/')

    def has_add_permission(self, request):
        return False # Remove botão "Add"
    
    def has_change_permission(self, request, obj=None):
        return False # Remove botão "Change"

# Registrando tudo
admin.site.register(Imovel, ImovelAdmin)
admin.site.register(Locacao, LocacaoAdmin)
admin.site.register(RelatorioGeral, RelatorioGeralAdmin)