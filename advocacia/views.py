from django.shortcuts import render, redirect
from django.db.models import Sum, Count, Q
from django.db.models.functions import ExtractMonth
from .models import FaturamentoAdvocacia, DespesaAdvocacia, ProcessoFaturamento
import datetime
from django.http import HttpResponse
import pandas as pd
import io

def relatorio_advocacia(request):
    ano_str = request.GET.get('ano')
    hoje = datetime.date.today()
    
    if ano_str:
        ano_str = str(ano_str).replace('.', '')
        ano = int(ano_str)
    else:
        ano = hoje.year

    # --- Consolidados Anuais ---
    faturamento_total = FaturamentoAdvocacia.objects.filter(data__year=ano).aggregate(Sum('valor'))['valor__sum'] or 0
    despesas_totais = DespesaAdvocacia.objects.filter(data__year=ano).aggregate(Sum('valor'))['valor__sum'] or 0
    lucro_total = faturamento_total - despesas_totais

    processos_qs = ProcessoFaturamento.objects.all()
    total_processos_historico = processos_qs.count()
    processos_ativos_total = processos_qs.filter(status__iexact='Ativo').count()
    processos_baixados_total = processos_qs.filter(status__iexact='Baixado').count()

    # --- Detalhamento Mensal ---
    meses_nomes = {
        1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril', 5: 'Maio', 6: 'Junho',
        7: 'Julho', 8: 'Agosto', 9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
    }

    fatu_mes = FaturamentoAdvocacia.objects.filter(data__year=ano).annotate(m=ExtractMonth('data')).values('m').annotate(total=Sum('valor'))
    desp_mes = DespesaAdvocacia.objects.filter(data__year=ano).annotate(m=ExtractMonth('data')).values('m').annotate(total=Sum('valor'))
    
    # Contagem mensal baseada no faturamento
    proc_mes = ProcessoFaturamento.objects.filter(faturamento__data__year=ano).annotate(
        m=ExtractMonth('faturamento__data')
    ).values('m').annotate(
        total=Count('id'),
        ativos=Count('id', filter=Q(status__iexact='Ativo')),
        baixados=Count('id', filter=Q(status__iexact='Baixado'))
    )

    fatu_dict = {item['m']: item['total'] for item in fatu_mes}
    desp_dict = {item['m']: item['total'] for item in desp_mes}
    proc_dict = {item['m']: item for item in proc_mes}

    meses_detalhes = []
    for i in range(12, 0, -1):
        f = fatu_dict.get(i, 0)
        d = desp_dict.get(i, 0)
        p = proc_dict.get(i, {'total': 0, 'ativos': 0, 'baixados': 0})
        
        if f > 0 or d > 0 or p['total'] > 0:
            meses_detalhes.append({
                'nome': meses_nomes[i],
                'faturamento': f,
                'despesa': d,
                'lucro': f - d,
                'proc_total': p['total'],
                'proc_ativos': p['ativos'],
                'proc_baixados': p['baixados'],
            })

    context = {
        'ano': ano,
        'faturamento': faturamento_total,
        'despesas': despesas_totais,
        'lucro': lucro_total,
        'total_processos': total_processos_historico,
        'processos_ativos': processos_ativos_total,
        'processos_baixados': processos_baixados_total,
        'meses_detalhes': meses_detalhes,
        'ano_anterior': ano - 1,
        'ano_proximo': ano + 1,
    }
    return render(request, 'relatorio_advocacia.html', context)

def download_advocacia_excel(request):
    ano_str = request.GET.get('ano', str(datetime.date.today().year)).replace('.', '')
    ano = int(ano_str)

    # Dados de Faturamento
    faturamentos = FaturamentoAdvocacia.objects.filter(data__year=ano)
    df_fatu = pd.DataFrame([{
        'Data': f.data.strftime('%d/%m/%Y'),
        'Cliente': f.cliente,
        'CPF/CNPJ': f.cpf_cnpj,
        'Valor (R$)': float(f.valor)
    } for f in faturamentos])
    
    # Dados de Despesas
    despesas = DespesaAdvocacia.objects.filter(data__year=ano)
    df_desp = pd.DataFrame([{
        'Data': d.data.strftime('%d/%m/%Y'),
        'Descrição': d.descricao,
        'Local': d.local,
        'Valor (R$)': float(d.valor)
    } for d in despesas])

    if df_fatu.empty and df_desp.empty:
        return HttpResponse("Não há dados para exportar neste ano.")

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        if not df_fatu.empty:
            df_fatu.to_excel(writer, index=False, sheet_name='Faturamentos')
        if not df_desp.empty:
            df_desp.to_excel(writer, index=False, sheet_name='Despesas')
    
    response = HttpResponse(output.getvalue(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename=Relatorio_Advocacia_{ano}.xlsx'
    return response

def download_advocacia_pdf(request):
    # Aciona a impressão do navegador com o layout já configurado no HTML
    return HttpResponse("<script>window.print(); window.history.back();</script>")