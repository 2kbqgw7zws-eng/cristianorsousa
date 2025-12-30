from django.contrib import admin
from django.shortcuts import redirect
from django.db.models import Sum
from django.db.models.functions import ExtractMonth
from import_export.admin import ImportExportModelAdmin
from import_export import resources
from .models import DespesaAdvocacia, FaturamentoAdvocacia, RelatorioAdvocacia, ProcessoFaturamento
import datetime

# --- RESOURCES ---
class DespesaResource(resources.ModelResource):
    class Meta:
        model = DespesaAdvocacia
        fields = ('id', 'data', 'descricao', 'local', 'valor')

class FaturamentoResource(resources.ModelResource):
    class Meta:
        model = FaturamentoAdvocacia
        fields = ('id', 'data', 'cliente', 'cpf_cnpj', 'valor')

# --- INLINES ---
class ProcessoInline(admin.TabularInline):
    model = ProcessoFaturamento
    extra = 1

# --- FUNÇÃO AUXILIAR DE FORMATAÇÃO ---
def formatar_brl(valor):
    """Converte float para string no padrão R$ 1.000,00"""
    return "{:,.2f}".format(valor).replace(',', 'X').replace('.', ',').replace('X', '.')

# --- CLASSES ADMIN ---

@admin.register(FaturamentoAdvocacia)
class FaturamentoAdmin(ImportExportModelAdmin):
    resource_class = FaturamentoResource
    change_list_template = 'admin/advocacia/faturamentoadvocacia/change_list.html'
    list_display = ('data', 'cliente', 'cpf_cnpj', 'valor')
    search_fields = ('cliente', 'cpf_cnpj')
    date_hierarchy = 'data'
    list_filter = ('data',)
    inlines = [ProcessoInline]

    def has_import_permission(self, request): return True

    def changelist_view(self, request, extra_context=None):
        hoje = datetime.date.today()
        ano_str = request.GET.get('data__year', str(hoje.year)).replace('.', '')
        ano_filtrado = int(ano_str)

        resumo_mensal = (
            FaturamentoAdvocacia.objects.filter(data__year=ano_filtrado)
            .annotate(mes=ExtractMonth('data')).values('mes')
            .annotate(total=Sum('valor')).order_by('mes')
        )

        meses_nomes = {1:'Jan', 2:'Fev', 3:'Mar', 4:'Abr', 5:'Mai', 6:'Jun',
                       7:'Jul', 8:'Ago', 9:'Set', 10:'Out', 11:'Nov', 12:'Dez'}
        
        # Inicializa com string "0,00"
        dados_resumo = {meses_nomes[m]: "0,00" for m in meses_nomes}
        total_geral = 0
        
        for item in resumo_mensal:
            if item['mes'] in meses_nomes:
                valor = float(item['total'] or 0)
                dados_resumo[meses_nomes[item['mes']]] = formatar_brl(valor)
                total_geral += valor

        extra_context = extra_context or {}
        extra_context.update({
            'resumo_financeiro': dados_resumo,
            'total_geral_ano': formatar_brl(total_geral),
            'ano_exibido': ano_filtrado,
            'metric_class': 'text-success' # Verde para Faturamento
        })
        return super().changelist_view(request, extra_context=extra_context)

@admin.register(DespesaAdvocacia)
class DespesaAdmin(ImportExportModelAdmin):
    resource_class = DespesaResource
    change_list_template = 'admin/advocacia/despesaadvocacia/change_list.html'
    list_display = ('data', 'descricao', 'local', 'valor')
    search_fields = ('descricao', 'local')
    date_hierarchy = 'data'
    list_filter = ('data',)

    def has_import_permission(self, request): return True

    def changelist_view(self, request, extra_context=None):
        hoje = datetime.date.today()
        ano_str = request.GET.get('data__year', str(hoje.year)).replace('.', '')
        ano_filtrado = int(ano_str)

        resumo_mensal = (
            DespesaAdvocacia.objects.filter(data__year=ano_filtrado)
            .annotate(mes=ExtractMonth('data')).values('mes')
            .annotate(total=Sum('valor')).order_by('mes')
        )

        meses_nomes = {1:'Jan', 2:'Fev', 3:'Mar', 4:'Abr', 5:'Mai', 6:'Jun',
                       7:'Jul', 8:'Ago', 9:'Set', 10:'Out', 11:'Nov', 12:'Dez'}
        
        # Inicializa com string "0,00"
        dados_resumo = {meses_nomes[m]: "0,00" for m in meses_nomes}
        total_geral = 0
        
        for item in resumo_mensal:
            if item['mes'] in meses_nomes:
                valor = float(item['total'] or 0)
                dados_resumo[meses_nomes[item['mes']]] = formatar_brl(valor)
                total_geral += valor

        extra_context = extra_context or {}
        extra_context.update({
            'resumo_financeiro': dados_resumo,
            'total_geral_ano': formatar_brl(total_geral),
            'ano_exibido': ano_filtrado,
            'metric_class': 'text-danger' # Vermelho para Despesas
        })
        return super().changelist_view(request, extra_context=extra_context)

@admin.register(RelatorioAdvocacia)
class RelatorioAdmin(admin.ModelAdmin):
    # Força o nome no menu lateral e título
    RelatorioAdvocacia._meta.verbose_name = "Visualizar Relatório Gerencial"
    RelatorioAdvocacia._meta.verbose_name_plural = "Visualizar Relatórios Gerencial"

    def changelist_view(self, request, extra_context=None):
        return redirect('relatorio_advocacia')
    
    def has_add_permission(self, request): return False
    def has_delete_permission(self, request, obj=None): return False