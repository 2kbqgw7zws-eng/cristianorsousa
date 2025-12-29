from django.shortcuts import render, redirect
from django.db.models import Sum
from .models import FaturamentoAdvocacia, DespesaAdvocacia, ProcessoFaturamento
import datetime
from django.http import HttpResponse
import pandas as pd

def relatorio_advocacia(request):
    ano_str = request.GET.get('ano')
    hoje = datetime.date.today()
    ano = int(ano_str) if ano_str else hoje.year

    # Financeiro
    faturamento = FaturamentoAdvocacia.objects.filter(data__year=ano).aggregate(Sum('valor'))['valor__sum'] or 0
    despesas = DespesaAdvocacia.objects.filter(data__year=ano).aggregate(Sum('valor'))['valor__sum'] or 0
    lucro = faturamento - despesas

    # Processos
    processos_qs = ProcessoFaturamento.objects.all()
    total_processos = processos_qs.count()
    # Filtros baseados no campo status (certifique-se que os nomes coincidem com o banco)
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

def download_advocacia_pdf(request):
    # Função temporária para evitar erro de URL até você configurar o PDF
    return HttpResponse("Função PDF em manutenção. O site voltou!")

def download_advocacia_excel(request):
    # Função temporária para evitar erro de URL até você configurar o Excel
    return HttpResponse("Função Excel em manutenção. O site voltou!")