from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Sum, Count, Avg, Max
from django.db.models.functions import TruncMonth
from .models import Imovel, Locacao, Despesa # <--- Importamos Despesa
import datetime
import openpyxl
from openpyxl.styles import Font, PatternFill
from django.template.loader import get_template
from xhtml2pdf import pisa

def buscar_dados_relatorio(ano_selecionado):
    hoje = datetime.date.today()
    inicio_ano = datetime.date(ano_selecionado, 1, 1)
    
    if ano_selecionado == hoje.year:
        fim_periodo = hoje
    elif ano_selecionado < hoje.year:
        fim_periodo = datetime.date(ano_selecionado, 12, 31)
    else:
        fim_periodo = inicio_ano

    dias_corridos_ano = (fim_periodo - inicio_ano).days + 1
    if dias_corridos_ano < 0: dias_corridos_ano = 0

    locacoes_ano = Locacao.objects.filter(data_entrada__year=ano_selecionado)
    despesas_ano = Despesa.objects.filter(data_pagamento__year=ano_selecionado)

    dados_imoveis = []
    imoveis = Imovel.objects.all()

    total_fat_geral = 0
    total_despesa_geral = 0
    total_dias_ocupados_geral = 0
    total_locacoes_geral = 0

    for imovel in imoveis:
        locs_imovel = locacoes_ano.filter(imovel=imovel)
        desps_imovel = despesas_ano.filter(imovel=imovel)
        
        # Cálculos de Locação
        dias_ocupados = 0
        faturamento = 0
        for loc in locs_imovel:
            if loc.data_saida and loc.data_entrada:
                dias = (loc.data_saida - loc.data_entrada).days
                if dias > 0: dias_ocupados += dias
            faturamento += loc.valor_cobrado_diaria or 0
        
        # Cálculos de Despesa e Lucro
        total_despesa = desps_imovel.aggregate(total=Sum('valor'))['total'] or 0
        lucro_liquido = faturamento - total_despesa
        
        dias_desocupados = dias_corridos_ano - dias_ocupados
        if dias_desocupados < 0: dias_desocupados = 0

        meses = locs_imovel.annotate(mes_ref=TruncMonth('data_entrada')).values('mes_ref').annotate(
            qtd=Count('id'), total=Sum('valor_cobrado_diaria'),
            media=Avg('valor_cobrado_diaria'), maior=Max('valor_cobrado_diaria')
        ).order_by('mes_ref')

        dados_imoveis.append({
            'nome': imovel.nome,
            'faturamento_total': faturamento,
            'total_despesa': total_despesa,
            'lucro_liquido': lucro_liquido,
            'dias_ocupados': dias_ocupados,
            'dias_desocupados': dias_desocupados,
            'total_locacoes': locs_imovel.count(),
            'ticket_medio': (faturamento / locs_imovel.count()) if locs_imovel.count() > 0 else 0,
            'meses': meses
        })

        total_fat_geral += faturamento
        total_despesa_geral += total_despesa
        total_dias_ocupados_geral += dias_ocupados
        total_locacoes_geral += locs_imovel.count()

    total_dias_potenciais = dias_corridos_ano * imoveis.count()
    total_dias_desocupados_geral = total_dias_potenciais - total_dias_ocupados_geral

    geral = {
        'total_faturado': total_fat_geral,
        'total_despesa': total_despesa_geral,
        'lucro_liquido': total_fat_geral - total_despesa_geral,
        'total_locacoes': total_locacoes_geral,
        'dias_ocupados': total_dias_ocupados_geral,
        'dias_desocupados': total_dias_desocupados_geral
    }
    
    return {
        'ano': ano_selecionado,
        'ano_anterior': ano_selecionado - 1,
        'ano_proximo': ano_selecionado + 1,
        'geral': geral,
        'dados_imoveis': dados_imoveis,
        'periodo_dias': dias_corridos_ano
    }

# --- As Views de Relatório, PDF e Excel continuam as mesmas da versão anterior ---
def relatorio_geral(request):
    hoje = datetime.date.today()
    try: ano = int(request.GET.get('ano', hoje.year))
    except ValueError: ano = hoje.year
    contexto = buscar_dados_relatorio(ano)
    return render(request, 'relatorio.html', contexto)

def download_relatorio_pdf(request):
    hoje = datetime.date.today()
    try: ano = int(request.GET.get('ano', hoje.year))
    except ValueError: ano = hoje.year
    contexto = buscar_dados_relatorio(ano)
    template_path = 'relatorio_pdf.html'
    template = get_template(template_path)
    html = template.render(contexto)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Relatorio_{ano}.pdf"'
    pisa.CreatePDF(html, dest=response)
    return response

def download_relatorio_excel(request):
    hoje = datetime.date.today()
    try: ano = int(request.GET.get('ano', hoje.year))
    except ValueError: ano = hoje.year
    dados = buscar_dados_relatorio(ano)
    wb = openpyxl.Workbook(); ws = wb.active
    ws.title = f"Relatorio {ano}"
    ws['A1'] = f"RELATÓRIO FINANCEIRO - {ano}"
    # (O restante do código do excel segue a mesma lógica de preencher as células)
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="Relatorio_{ano}.xlsx"'
    wb.save(response)
    return response