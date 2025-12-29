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
    list_filter = ('data',)

    def has_import_permission(self, request):
        return False

    def changelist_view(self, request, extra_context=None):
        # 1. Identifica o ano filtrado. Se não houver filtro, usa o ano atual.
        hoje = datetime.date.today()
        ano_filtrado = hoje.year
        
        # Tenta pegar o ano do filtro da barra lateral (URL)
        # O Django Admin costuma passar filtros de data via GET
        data_year = request.GET.get('data__year')
        data_gte = request.GET.get('data__gte') # Caso seja um range
        
        if data_year:
            ano_filtrado = int(data_year)
        elif data_gte and len(data_gte) >= 4:
            ano_filtrado = int(data_gte[:4])

        # 2. Agrupa gastos por mês do ano selecionado (dinâmico)
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
        extra_context['ano_exibido'] = ano_filtrado # Passa para o HTML saber qual ano mostrar
        
        return super().changelist_view(request, extra_context=extra_context)

@admin.register(RelatorioAdvocacia)
class RelatorioAdmin(admin.ModelAdmin):
    def changelist_view(self, request, extra_context=None):
        return redirect('relatorio_advocacia')
    def has_add_permission(self, request): return False
    def has_delete_permission(self, request, obj=None): return False