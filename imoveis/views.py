from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Sum, Count, Avg, Max
from django.db.models.functions import TruncMonth
from .models import Imovel, Locacao, Despesa 
import datetime

def buscar_dados_relatorio(ano_selecionado):
    hoje = datetime.date.today()
    inicio_ano = datetime.date(ano_selecionado, 1, 1)
    fim_periodo = hoje if ano_selecionado == hoje.year else datetime.date(ano_selecionado, 12, 31)
    
    dias_corridos_ano = (fim_periodo - inicio_ano).days + 1
    
    locacoes_ano = Locacao.objects.filter(data_entrada__year=ano_selecionado)
    despesas_ano = Despesa.objects.filter(data_pagamento__year=ano_selecionado)

    dados_imoveis = []
    imoveis = Imovel.objects.all()
    total_fat_geral = 0
    total_despesa_geral = 0

    for imovel in imoveis:
        locs_imovel = locacoes_ano.filter(imovel=imovel)
        desps_imovel = despesas_ano.filter(imovel=imovel)
        
        faturamento = locs_imovel.aggregate(Sum('valor_cobrado_diaria'))['valor_cobrado_diaria__sum'] or 0
        total_despesa = desps_imovel.aggregate(Sum('valor'))['valor__sum'] or 0
        
        # Cálculo de dias ocupados (saída - entrada)
        dias_ocupados = 0
        for loc in locs_imovel:
            dias = (loc.data_saida - loc.data_entrada).days
            if dias > 0: dias_ocupados += dias

        dados_imoveis.append({
            'nome': imovel.nome,
            'faturamento_total': faturamento,
            'total_despesa': total_despesa,
            'lucro_liquido': faturamento - total_despesa,
            'dias_ocupados': dias_ocupados,
            'dias_desocupados': max(0, dias_corridos_ano - dias_ocupados),
            'total_locacoes': locs_imovel.count(),
            'ticket_medio': (faturamento / locs_imovel.count()) if locs_imovel.count() > 0 else 0,
            'meses': locs_imovel.annotate(mes_ref=TruncMonth('data_entrada')).values('mes_ref').annotate(
                qtd=Count('id'), total=Sum('valor_cobrado_diaria'), media=Avg('valor_cobrado_diaria')
            ).order_by('mes_ref')
        })
        total_fat_geral += faturamento
        total_despesa_geral += total_despesa

    return {
        'ano': ano_selecionado,
        'ano_anterior': ano_selecionado - 1,
        'ano_proximo': ano_selecionado + 1,
        'geral': {
            'total_faturado': total_fat_geral,
            'total_despesa': total_despesa_geral,
            'lucro_liquido': total_fat_geral - total_despesa_geral,
            'total_locacoes': locacoes_ano.count(),
        },
        'dados_imoveis': dados_imoveis,
        'periodo_dias': dias_corridos_ano
    }
# Mantenha as outras funções (relatorio_geral, pdf, excel) abaixo...