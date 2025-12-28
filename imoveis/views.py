from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Sum, Count, Avg, Max
from django.db.models.functions import TruncMonth
from .models import Imovel, Locacao, Despesa 
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

    # Mantemos o filtro por ano apenas para o cálculo do resumo financeiro anual
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
        
        dias_ocupados = 0
        faturamento = 0
        for loc in locs_imovel:
            if loc.data_saida and loc.data_entrada:
                dias = (loc.data_saida - loc.data_entrada).days
                if dias > 0: dias_ocupados += dias
            faturamento += loc.valor_cobrado_diaria or 0
        
        total_despesa = desps_imovel.aggregate(total=Sum('valor'))['total'] or 0
        lucro_liquido = faturamento - total_despesa
        
        if imovel.valor_compra and imovel.valor_compra > 0:
            porcentagem_lucro = (lucro_liquido / imovel.valor_compra) * 100
        else:
            porcentagem_lucro = 0
        
        meses = locs_imovel.annotate(mes_ref=TruncMonth('data_entrada')).values('mes_ref').annotate(
            qtd=Count('id'), total=Sum('valor_cobrado_diaria'),
            media=Avg('valor_cobrado_diaria'), maior=Max('valor_cobrado_diaria')
        ).order_by('mes_ref')

        dados_imoveis.append({
            'nome': imovel.nome,
            'faturamento_total': faturamento,
            'total_despesa': total_despesa,
            'lucro_liquido': lucro_liquido,
            'porcentagem_lucro': porcentagem_lucro,
            'dias_ocupados': dias_ocupados,
            'dias_desocupados': max(0, dias_corridos_ano - dias_ocupados),
            'total_locacoes': locs_imovel.count(),
            'ticket_medio': (faturamento / locs_imovel.count()) if locs_imovel.count() > 0 else 0,
            'meses': meses,
            # ALTERAÇÃO: Pegamos todas as locações do imóvel (incluindo 2026) para o PDF
            'locacoes_detalhadas': Locacao.objects.filter(imovel=imovel).order_by('data_entrada')
        })

        total_fat_geral += faturamento
        total_despesa_geral += total_despesa
        total_dias_ocupados_geral += dias_ocupados
        total_locacoes_geral += locs_imovel.count()

    geral = {
        'total_faturado': total_fat_geral,
        'total_despesa': total_despesa_geral,
        'lucro_liquido': total_fat_geral - total_despesa_geral,
        'total_locacoes': total_locacoes_geral,
        'dias_ocupados': total_dias_ocupados_geral,
        'dias_desocupados': (dias_corridos_ano * imoveis.count()) - total_dias_ocupados_geral
    }
    
    return {
        'ano': ano_selecionado,
        'ano_anterior': ano_selecionado - 1,
        'ano_proximo': ano_selecionado + 1,
        'geral': geral,
        'dados_imoveis': dados_imoveis,
        'periodo_dias': dias_corridos_ano
    }

def relatorio_geral(request):
    hoje = datetime.date.today()
    try:
        ano = int(request.GET.get('ano', hoje.year))
    except ValueError:
        ano = hoje.year
    contexto = buscar_dados_relatorio(ano)
    return render(request, 'relatorio.html', contexto)

def download_relatorio_pdf(request):
    hoje = datetime.date.today()
    try: ano = int(request.GET.get('ano', hoje.year))
    except ValueError: ano = hoje.year
    
    contexto = buscar_dados_relatorio(ano)
    
    # Recalculamos o resumo geral para o PDF considerar TUDO e não só o ano selecionado
    todas_locacoes = Locacao.objects.all()
    contexto['geral']['total_faturado'] = todas_locacoes.aggregate(Sum('valor_cobrado_diaria'))['valor_cobrado_diaria__sum'] or 0
    contexto['geral']['total_locacoes'] = todas_locacoes.count()
    contexto['ano'] = "Geral (Consolidado)"

    template = get_template('relatorio_pdf.html')
    html = template.render(contexto)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Relatorio_Geral_Locacoes.pdf"'
    pisa.CreatePDF(html, dest=response)
    return response

def download_relatorio_excel(request):
    # ALTERAÇÃO: Busca todas as locações existentes no sistema, sem filtro de ano
    locacoes = Locacao.objects.all().order_by('data_entrada')
    
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Todas as Locações"
    
    colunas = ['IMÓVEL', 'CLIENTE', 'CPF', 'TELEFONE', 'DATA ENTRADA', 'DATA SAÍDA']
    ws.append(colunas)
    
    for cell in ws[1]:
        cell.font = Font(bold=True)
        cell.fill = PatternFill(start_color="DDDDDD", end_color="DDDDDD", fill_type="solid")

    for loc in locacoes:
        ws.append([
            loc.imovel.nome,
            loc.cliente,
            loc.cpf,
            loc.telefone,
            loc.data_entrada.strftime('%d/%m/%Y'),
            loc.data_saida.strftime('%d/%m/%Y')
        ])

    for col in ws.columns:
        max_length = 0
        column = col[0].column_letter
        for cell in col:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except: pass
        ws.column_dimensions[column].width = max_length + 2

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="Relatorio_Completo_Locacoes.xlsx"'
    wb.save(response)
    return response