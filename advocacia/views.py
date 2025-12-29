from django.shortcuts import render
from django.db.models import Sum
from django.db.models.functions import ExtractMonth
from .models import FaturamentoAdvocacia, DespesaAdvocacia, ProcessoFaturamento
import datetime

def relatorio_advocacia(request):
    ano_str = request.GET.get('ano')
    hoje = datetime.date.today()
    ano = int(ano_str) if ano_str else hoje.year

    # --- Consolidados Anuais ---
    faturamento_total = FaturamentoAdvocacia.objects.filter(data__year=ano).aggregate(Sum('valor'))['valor__sum'] or 0
    despesas_totais = DespesaAdvocacia.objects.filter(data__year=ano).aggregate(Sum('valor'))['valor__sum'] or 0
    lucro_total = faturamento_total - despesas_totais

    processos_qs = ProcessoFaturamento.objects.all()
    total_processos = processos_qs.count()
    processos_ativos = processos_qs.filter(status__iexact='Ativo').count()
    processos_baixados = processos_qs.filter(status__iexact='Baixado').count()

    # --- Régua de Meses Detalhada ---
    meses_nomes = {
        1: 'Jan', 2: 'Fev', 3: 'Mar', 4: 'Abr', 5: 'Mai', 6: 'Jun',
        7: 'Jul', 8: 'Ago', 9: 'Set', 10: 'Out', 11: 'Nov', 12: 'Dez'
    }

    faturamento_mes = FaturamentoAdvocacia.objects.filter(data__year=ano).annotate(
        m=ExtractMonth('data')).values('m').annotate(total=Sum('valor'))
    despesa_mes = DespesaAdvocacia.objects.filter(data__year=ano).annotate(
        m=ExtractMonth('data')).values('m').annotate(total=Sum('valor'))

    fatu_dict = {item['m']: item['total'] for item in faturamento_mes}
    desp_dict = {item['m']: item['total'] for item in despesa_mes}

    meses_detalhes = []
    for i in range(1, 13):
        f = fatu_dict.get(i, 0)
        d = desp_dict.get(i, 0)
        meses_detalhes.append({
            'nome': meses_nomes[i],
            'faturamento': f,
            'despesa': d,
            'lucro': f - d
        })

    context = {
        'ano': ano,
        'ano_anterior': ano - 1,
        'ano_proximo': ano + 1,
        'faturamento': faturamento_total,
        'despesas': despesas_totais,
        'lucro': lucro_total,
        'total_processos': total_processos,
        'processos_ativos': processos_ativos,
        'processos_baixados': processos_baixados,
        'meses_detalhes': meses_detalhes,
    }
    return render(request, 'relatorio_advocacia.html', context)