from django.contrib import admin
from django.shortcuts import redirect
from django.db.models import Sum
from django.db.models.functions import ExtractMonth
from import_export.admin import ImportExportModelAdmin
from .models import DespesaAdvocacia, FaturamentoAdvocacia, RelatorioAdvocacia, ProcessoFaturamento
import datetime

# Configuração para os processos aparecerem dentro do faturamento
class ProcessoInline(admin.TabularInline):
    model = ProcessoFaturamento
    extra = 1

@admin.register(FaturamentoAdvocacia)
class FaturamentoAdmin(admin.ModelAdmin):
    list_display = ('data', 'cliente', 'cpf_cnpj', 'valor')
    search_fields = ('cliente', 'cpf_cnpj')
    inlines = [ProcessoInline]

@admin.register(DespesaAdvocacia)
class DespesaAdmin(ImportExportModelAdmin):
    list_display = ('data', 'descricao', 'local', 'valor')
    search_fields = ('descricao', 'local')
    list_filter = ('data',)

    # Esconde o botão de importar para manter a interface limpa
    def has_import_permission(self, request):
        return False

    def changelist_view(self, request, extra_context=None):
        """Adiciona o cálculo mensal ao topo da página de Despesas"""
        hoje = datetime.date.today()
        # Filtra as despesas do ano atual
        resumo_mensal = (
            DespesaAdvocacia.objects.filter(data__year=hoje.year)
            .annotate(mes=ExtractMonth('data'))
            .values('mes')
            .annotate(total=Sum('valor'))
            .order_by('mes')
        )

        # Nomes dos meses para exibição
        meses_nomes = {
            1: 'Jan', 2: 'Fev', 3: 'Mar', 4: 'Abr', 5: 'Mai', 6: 'Jun',
            7: 'Jul', 8: 'Ago', 9: 'Set', 10: 'Out', 11: 'Nov', 12: 'Dez'
        }
        
        # Inicializa todos os meses com zero
        dados_resumo = {meses_nomes[m]: 0 for m in meses_nomes}
        total_geral = 0
        
        for item in resumo_mensal:
            nome_mes = meses_nomes[item['mes']]
            valor = item['total']
            dados_resumo[nome_mes] = valor
            total_geral += valor

        # Envia os dados para o template customizado
        extra_context = extra_context or {}
        extra_context['resumo_financeiro'] = dados_resumo
        extra_context['total_geral_ano'] = total_geral
        
        return super().changelist_view(request, extra_context=extra_context)

@admin.register(RelatorioAdvocacia)
class RelatorioAdmin(admin.ModelAdmin):
    def changelist_view(self, request, extra_context=None):
        return redirect('relatorio_advocacia')
    
    def has_add_permission(self, request): return False
    def has_delete_permission(self, request, obj=None): return False