from django.contrib import admin
from django.shortcuts import redirect
from django.db.models import Sum
from django.db.models.functions import ExtractMonth
from import_export.admin import ImportExportModelAdmin
from import_export import resources  # IMPORTANTE PARA A IMPORTAÇÃO
from .models import DespesaAdvocacia, FaturamentoAdvocacia, RelatorioAdvocacia, ProcessoFaturamento
import datetime

# --- CONFIGURAÇÃO DE RECURSOS PARA IMPORTAÇÃO/EXPORTAÇÃO ---

class DespesaResource(resources.ModelResource):
    class Meta:
        model = DespesaAdvocacia
        # Define os campos que o Excel deve ter
        fields = ('id', 'data', 'descricao', 'local', 'valor')
        export_order = ('id', 'data', 'descricao', 'local', 'valor')

# --- INLINES ---

class ProcessoInline(admin.TabularInline):
    model = ProcessoFaturamento
    extra = 1

# --- CLASSES ADMIN ---

@admin.register(FaturamentoAdvocacia)
class FaturamentoAdmin(admin.ModelAdmin):
    list_display = ('data', 'cliente', 'cpf_cnpj', 'valor')
    search_fields = ('cliente', 'cpf_cnpj')
    inlines = [ProcessoInline]

@admin.register(DespesaAdvocacia)
class DespesaAdmin(ImportExportModelAdmin):
    # Liga o mapeador de Excel a esta tela
    resource_class = DespesaResource
    
    change_list_template = 'admin/advocacia/despesaadvocacia/change_list.html'
    
    list_display = ('data', 'descricao', 'local', 'valor')
    search_fields = ('descricao', 'local')
    date_hierarchy = 'data' 
    list_filter = ('data',)

    # AGORA TRUE: Habilita o botão "Importar" no topo da página
    def has_import_permission(self, request):
        return True

    def changelist_view(self, request, extra_context=None):
        hoje = datetime.date.today()
        
        # Lógica de detecção de ano para o resumo mensal
        ano_filtrado = request.GET.get('data__year')
        if not ano_filtrado:
            data_gte = request.GET.get('data__gte')
            if data_gte:
                ano_filtrado = data_gte[:4]
            else:
                ano_filtrado = hoje.year
        
        ano_filtrado = int(ano_filtrado)

        # Cálculo do resumo mensal
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