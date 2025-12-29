from django.db.models import Sum
from .models import FaturamentoAdvocacia, DespesaAdvocacia, ProcessoFaturamento
import datetime

def relatorio_advocacia(request):
    # Captura o ano da URL ou usa o atual
    ano_str = request.GET.get('ano')
    hoje = datetime.date.today()
    ano = int(ano_str) if ano_str else hoje.year

    # Cálculos Financeiros do Ano
    faturamento = FaturamentoAdvocacia.objects.filter(data__year=ano).aggregate(Sum('valor'))['valor__sum'] or 0
    despesas = DespesaAdvocacia.objects.filter(data__year=ano).aggregate(Sum('valor'))['valor__sum'] or 0
    lucro = faturamento - despesas

    # Indicadores de Processos (Total histórico e Status)
    # Nota: Certifique-se de que o campo 'status' existe no seu modelo ProcessoFaturamento
    processos_qs = ProcessoFaturamento.objects.all()
    total_processos = processos_qs.count()
    processos_ativos = processos_qs.filter(status__iexact='Ativo').count()
    processos_baixados = processos_qs.filter(status__iexact='Baixado').count()

    context = {
        'ano': ano,
        'ano_anterior': ano - 1,
        'ano_proximo': ano + 1,
        'faturamento': faturamento,
        'despesas': despesas,
        'lucro': lucro,
        'total_processos': total_processos,
        'processos_ativos': processos_ativos,
        'processos_baixados': processos_baixados,
    }
    return render(request, 'relatorio_advocacia.html', context)