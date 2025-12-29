from django.shortcuts import render, redirect
from django.db.models import Sum
from django.db.models.functions import ExtractMonth
from .models import FaturamentoAdvocacia, DespesaAdvocacia, ProcessoFaturamento
import datetime
from django.http import HttpResponse
import pandas as pd
import io

def relatorio_advocacia(request):
    ano_str = request.GET.get('ano')
    hoje = datetime.date.today()
    ano = int(ano_str) if ano_str else hoje.year

    faturamento_total = FaturamentoAdvocacia.objects.filter(data__year=ano).aggregate(Sum('valor'))['valor__sum'] or 0
    despesas_totais = DespesaAdvocacia.objects.filter(data__year=ano).aggregate(Sum('valor'))['valor__sum'] or 0
    lucro_total = faturamento_total - despesas_totais

    processos_qs = ProcessoFaturamento.objects.all()
    total_processos = processos_qs.count()
    processos_ativos = processos_qs.filter(status__iexact='Ativo').count()
    processos_baixados = processos_qs.filter(status__iexact='Baixado').count()

    meses_nomes = {
        1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril', 5: 'Maio', 6: 'Junho',
        7: 'Julho', 8: 'Agosto', 9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
    }

    fatu_mes = FaturamentoAdvocacia.objects.filter(data__year=ano).annotate(m=ExtractMonth('data')).values('m').annotate(total=Sum('valor'))
    desp_mes = DespesaAdvocacia.objects.filter(data__year=ano).annotate(m=ExtractMonth('data')).values('m').annotate(total=Sum('valor'))

    fatu_dict = {item['m']: item['total'] for item in fatu_mes}
    desp_dict = {item['m']: item['total'] for item in desp_mes}

    meses_detalhes = []
    # De Dezembro para Janeiro para mostrar o mais recente primeiro
    for i in range(12, 0, -1):
        f = fatu_dict.get(i, 0)
        d = desp_dict.get(i, 0)
        if f > 0 or d > 0: # Só mostra meses com movimento
            meses_detalhes.append({
                'nome': meses_nomes[i],
                'faturamento': f,
                'despesa': d,
                'lucro': f - d
            })

    context = {
        'ano': ano, 'ano_anterior': ano - 1, 'ano_proximo': ano + 1,
        'faturamento': faturamento_total, 'despesas': despesas_totais, 'lucro': lucro_total,
        'total_processos': total_processos, 'processos_ativos': processos_ativos,
        'processos_baixados': processos_baixados, 'meses_detalhes': meses_detalhes,
    }
    return render(request, 'relatorio_advocacia.html', context)

def download_advocacia_excel(request):
    ano = request.GET.get('ano', datetime.date.today().year)
    # Lógica simplificada de exportação usando Pandas
    data = []
    faturamentos = FaturamentoAdvocacia.objects.filter(data__year=ano)
    for f in faturamentos:
        data.append({'Tipo': 'Faturamento', 'Data': f.data, 'Desc': f.cliente, 'Valor': f.valor})
    
    despesas = DespesaAdvocacia.objects.filter(data__year=ano)
    for d in despesas:
        data.append({'Tipo': 'Despesa', 'Data': d.data, 'Desc': d.descricao, 'Valor': d.valor})

    df = pd.DataFrame(data)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Relatorio')
    
    response = HttpResponse(output.getvalue(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename=Relatorio_Advocacia_{ano}.xlsx'
    return response

def download_advocacia_pdf(request):
    # Para o PDF, uma solução rápida é retornar um HTML formatado para impressão
    # Ou você pode integrar o WeasyPrint/ReportLab. Aqui retornamos um aviso de trigger de impressão.
    return HttpResponse("Função de PDF: Use Ctrl+P na página do relatório para salvar como PDF formatado.")