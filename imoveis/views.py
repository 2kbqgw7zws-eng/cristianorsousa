from django.shortcuts import render
from django.db.models import Sum, Count, Avg, Max
from django.db.models.functions import TruncMonth
from .models import Imovel, Locacao
import datetime

def relatorio_geral(request):
    # 1. Descobrir qual ano o usuário quer ver
    hoje = datetime.date.today()
    ano_atual_sistema = hoje.year
    
    # Tenta pegar o ano da URL (?ano=2026), se não der, usa o ano atual
    ano_url = request.GET.get('ano')
    try:
        ano_selecionado = int(ano_url) if ano_url else ano_atual_sistema
    except ValueError:
        ano_selecionado = ano_atual_sistema

    # 2. Filtrar locações pelo ano selecionado
    locacoes_ano = Locacao.objects.filter(
        data_entrada__year=ano_selecionado
    )

    # 3. Cálculos Gerais (KPIs do Topo)
    geral = locacoes_ano.aggregate(
        total_faturado=Sum('valor_cobrado_diaria'),
        total_locacoes=Count('id'),
        ticket_medio=Avg('valor_cobrado_diaria'),
        dias_ocupados=Count('data_entrada') 
    )

    # 4. Dados por Imóvel
    dados_imoveis = []
    imoveis = Imovel.objects.all()

    for imovel in imoveis:
        # Filtra locações desse imóvel NO ANO SELECIONADO
        locs_imovel = locacoes_ano.filter(imovel=imovel)
        
        resumo_imovel = locs_imovel.aggregate(
            fat=Sum('valor_cobrado_diaria'),
            dias=Count('id')
        )

        meses = locs_imovel.annotate(
            mes_ref=TruncMonth('data_entrada')
        ).values('mes_ref').annotate(
            qtd=Count('id'),
            total=Sum('valor_cobrado_diaria'),
            media=Avg('valor_cobrado_diaria'),
            maior=Max('valor_cobrado_diaria')
        ).order_by('mes_ref')

        dados_imoveis.append({
            'nome': imovel.nome,
            'faturamento_total': resumo_imovel['fat'] or 0,
            'dias_ocupados': resumo_imovel['dias'] or 0,
            'meses': meses
        })

    # 5. Enviar para o HTML (incluindo variáveis para os botões de próximo/anterior)
    return render(request, 'relatorio.html', {
        'ano': ano_selecionado,
        'ano_anterior': ano_selecionado - 1,
        'ano_proximo': ano_selecionado + 1,
        'geral': geral,
        'dados_imoveis': dados_imoveis
    })