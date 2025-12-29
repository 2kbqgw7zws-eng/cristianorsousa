from django.contrib import admin
from django.shortcuts import redirect
from django.db.models import Sum
from django.db.models.functions import ExtractMonth
from import_export.admin import ImportExportModelAdmin
from .models import DespesaAdvocacia, FaturamentoAdvocacia, RelatorioAdvocacia, ProcessoFaturamento
import datetime

# Inline para Processos dentro de Faturamento
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
    change_list_template = 'admin/advocacia/despesaadvocacia/change_list.html'
    
    list_display = ('data', 'descricao', 'local', 'valor')
    search_fields = ('descricao', 'local')
    # O list_filter abaixo gera a barra lateral para trocar de ano
    list_filter = ('data',)

    def has_import_permission(self, request):
        return False

    def changelist_view(self, request, extra_context=None):
        hoje = datetime.date.today()
        
        # Pega o ano da URL (filtro lateral). Se não tiver, usa o ano atual.
        query_params = request.GET
        ano_filtrado = hoje.year
        
        for key, value in query_params.items():
            if 'data__year' in key:
                ano_filtrado = int(value)
                break
            elif 'data__gte' in key: # Filtro de "Este ano" ou "Ano passado"
                ano_filtrado = int(value[:4])
                break

        # Agrupa gastos por mês do ano selecionado
        resumo_mensal = (
            DespesaAdvocacia.objects.filter(data__year=ano_filtrado)
            .annotate(mes=ExtractMonth('data'))
            .values('mes')
            .annotate(total=Sum('valor'))
            .order_by('mes')
        )

        meses_nomes = {
            1: 'Jan', 2: 'Fev', 3: 'Mar', 4: 'Abr', 5: 'Mai', 6: 'Jun',
            7: 'Jul', 8: 'Ago', 9: 'Set', 10: 'Out', 11: 'Nov', 12: 'Dez'
        }
        
        dados_resumo = {meses_nomes[m]: 0 for m in meses_nomes}
        total_geral = 0
        
        for item in resumo_mensal:
            if item['mes'] in meses_nomes:
                nome_mes = meses_nomes[item['mes']]
                valor = item['total'] or 0
                dados_resumo[nome_mes] = valor
                total_geral += valor

        extra_context = extra_context or {}
        extra_context['resumo_financeiro'] = dados_resumo
        extra_context['total_geral_ano'] = total_geral
        extra_context['ano_exibido'] = ano_filtrado
        
        return super().changelist_view(request, extra_context=extra_context)

@admin.register(RelatorioAdvocacia)
class RelatorioAdmin(admin.ModelAdmin):
    def changelist_view(self, request, extra_context=None):
        return redirect('relatorio_advocacia')
    def has_add_permission(self, request): return False
    def has_delete_permission(self, request, obj=None): return False