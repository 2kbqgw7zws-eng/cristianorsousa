from django.contrib import admin
from django.shortcuts import redirect
from django.db.models import Sum
from django.db.models.functions import ExtractMonth
from import_export.admin import ImportExportModelAdmin
from import_export import resources
from .models import DespesaAdvocacia, FaturamentoAdvocacia, RelatorioAdvocacia, ProcessoFaturamento
import datetime

# --- RESOURCES (Import/Export) ---
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

# --- FUNÇÃO AUXILIAR ---
def formatar_brl(valor):
    """Converte float para string R$ 1.000,00"""
    try:
        return "{:,.2f}".format(valor).replace(',', 'X').replace('.', ',').replace('X', '.')
    except:
        return "0,00"

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

    def has_import_permission(self, request): 
        return True

    def changelist_view(self, request, extra_context=None):
        # 1. Determinar o ano (filtro ou ano atual)
        hoje = datetime.date.today()
        ano_str = request.GET.get('data__year', str(hoje.year))
        # Remove pontos caso venha formatado e converte para int
        try:
            ano_filtrado = int(ano_str.replace('.', ''))
        except ValueError:
            ano_filtrado = hoje.year

        # 2. Consultar o banco de dados
        resumo_mensal = (
            FaturamentoAdvocacia.objects.filter(data__year=ano_filtrado)
            .annotate(mes=ExtractMonth('data'))
            .values('mes')
            .annotate(total=Sum('valor'))
            .order_by('mes')
        )

        # 3. Preparar estrutura de dados (Janeiro a Dezembro zerados)
        meses_nomes = {
            1:'Jan', 2:'Fev', 3:'Mar', 4:'Abr', 5:'Mai', 6:'Jun',
            7:'Jul', 8:'Ago', 9:'Set', 10:'Out', 11:'Nov', 12:'Dez'
        }
        
        dados_resumo = {meses_nomes[m]: 0 for m in meses_nomes}
        total_geral = 0

        # 4. Preencher com os dados do banco
        for item in resumo_mensal:
            mes_numero = item['mes']
            if mes_numero in meses_nomes:
                valor = float(item['total'] or 0)
                dados_resumo[meses_nomes[mes_numero]] = valor
                total_geral += valor

        # 5. Enviar para o template
        extra_context = extra_context or {}
        extra_context.update({
            'resumo_financeiro': dados_resumo,
            'total_geral_ano': formatar_brl(total_geral),
            'ano_exibido': ano_filtrado,
            'metric_class': 'text-success' # Verde para faturamento
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

    def has_import_permission(self, request): 
        return True

    def changelist_view(self, request, extra_context=None):
        # 1. Determinar o ano
        hoje = datetime.date.today()
        ano_str = request.GET.get('data__year', str(hoje.year))
        try:
            ano_filtrado = int(ano_str.replace('.', ''))
        except ValueError:
            ano_filtrado = hoje.year

        # 2. Consultar o banco
        resumo_mensal = (
            DespesaAdvocacia.objects.filter(data__year=ano_filtrado)
            .annotate(mes=ExtractMonth('data'))
            .values('mes')
            .annotate(total=Sum('valor'))
            .order_by('mes')
        )

        # 3. Estrutura de dados
        meses_nomes = {
            1:'Jan', 2:'Fev', 3:'Mar', 4:'Abr', 5:'Mai', 6:'Jun',
            7:'Jul', 8:'Ago', 9:'Set', 10:'Out', 11:'Nov', 12:'Dez'
        }
        
        dados_resumo = {meses_nomes[m]: 0 for m in meses_nomes}
        total_geral = 0

        # 4. Preencher dados
        for item in resumo_mensal:
            mes_numero = item['mes']
            if mes_numero in meses_nomes:
                valor = float(item['total'] or 0)
                dados_resumo[meses_nomes[mes_numero]] = valor
                total_geral += valor

        # 5. Enviar para template
        extra_context = extra_context or {}
        extra_context.update({
            'resumo_financeiro': dados_resumo,
            'total_geral_ano': formatar_brl(total_geral),
            'ano_exibido': ano_filtrado,
            'metric_class': 'text-danger' # Vermelho para despesas
        })

        return super().changelist_view(request, extra_context=extra_context)


@admin.register(RelatorioAdvocacia)
class RelatorioAdmin(admin.ModelAdmin):
    def changelist_view(self, request, extra_context=None):
        return redirect('relatorio_advocacia')
    
    def has_add_permission(self, request): 
        return False
    
    def has_delete_permission(self, request, obj=None): 
        return False