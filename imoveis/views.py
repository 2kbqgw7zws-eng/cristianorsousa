from django.shortcuts import render
from django.db.models import Avg, Max, Min, Count, Sum
from django.db.models.functions import TruncMonth
from .models import Locacao, Imovel

def relatorio_financeiro(request):
    # AGORA PEGAMOS TUDO (Removemos o filtro de ano)
    todas_locacoes = Locacao.objects.all()
    
    # Cálculo manual do faturamento total geral
    faturamento_geral = 0
    dias_ocupados_geral = 0
    for loc in todas_locacoes:
        dias = (loc.data_saida - loc.data_entrada).days
        # Evitar dias negativos ou zero se a pessoa sair no mesmo dia
        if dias <= 0: dias = 1 
        faturamento_geral += dias * loc.valor_cobrado_diaria
        dias_ocupados_geral += dias

    # Evita erro de divisão por zero se não tiver locações
    ticket_medio = 0
    if todas_locacoes.count() > 0:
        ticket_medio = todas_locacoes.aggregate(Avg('valor_cobrado_diaria'))['valor_cobrado_diaria__avg']

    resumo_geral = {
        'total_faturado': faturamento_geral,
        'dias_ocupados': dias_ocupados_geral,
        'ticket_medio': ticket_medio,
        'total_locacoes': todas_locacoes.count()
    }

    # --- PARTE 2: DADOS POR IMÓVEL ---
    dados_por_imovel = []
    imoveis = Imovel.objects.all()

    for imovel in imoveis:
        # Pega todas as locações deste imóvel (sem filtro de ano)
        locacoes_imovel = Locacao.objects.filter(imovel=imovel)
        
        if not locacoes_imovel.exists():
            continue

        fat_imovel = 0
        dias_imovel = 0
        for loc in locacoes_imovel:
            dias = (loc.data_saida - loc.data_entrada).days
            if dias <= 0: dias = 1
            fat_imovel += dias * loc.valor_cobrado_diaria
            dias_imovel += dias

        meses = locacoes_imovel.annotate(
            mes_ref=TruncMonth('data_entrada')
        ).values('mes_ref').annotate(
            media=Avg('valor_cobrado_diaria'),
            maior=Max('valor_cobrado_diaria'),
            qtd=Count('id')
        ).order_by('-mes_ref') # Ordena do mais recente para o antigo

        dados_por_imovel.append({
            'nome': imovel.nome,
            'faturamento_total': fat_imovel,
            'dias_ocupados': dias_imovel,
            'meses': meses
        })

    return render(request, 'relatorio.html', {
        'geral': resumo_geral,
        'dados_imoveis': dados_por_imovel,
    })