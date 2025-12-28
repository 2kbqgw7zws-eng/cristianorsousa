from django.shortcuts import render
from django.db.models import Sum, Count, Avg, Max
from django.db.models.functions import TruncMonth
from .models import Imovel, Locacao
import datetime

def relatorio_geral(request):
    hoje = datetime.date.today()
    ano_atual = hoje.year
    
    locacoes_ano = Locacao.objects.filter(data_entrada__year=ano_atual)

    geral = locacoes_ano.aggregate(
        total_faturado=Sum('valor_cobrado_diaria'),
        total_locacoes=Count('id'),
        ticket_medio=Avg('valor_cobrado_diaria'),
        dias_ocupados=Count('data_entrada')
    )

    dados_imoveis = []
    imoveis = Imovel.objects.all()

    for imovel in imoveis:
        locs_imovel = locacoes_ano.filter(imovel=imovel)
        resumo_imovel = locs_imovel.aggregate(fat=Sum('valor_cobrado_diaria'), dias=Count('id'))
        
        meses = locs_imovel.annotate(mes_ref=TruncMonth('data_entrada')).values('mes_ref').annotate(
            qtd=Count('id'), total=Sum('valor_cobrado_diaria'),
            media=Avg('valor_cobrado_diaria'), maior=Max('valor_cobrado_diaria')
        ).order_by('mes_ref')

        dados_imoveis.append({
            'nome': imovel.nome,
            'faturamento_total': resumo_imovel['fat'] or 0,
            'dias_ocupados': resumo_imovel['dias'] or 0,
            'meses': meses
        })

    return render(request, 'relatorio.html', {
        'ano': ano_atual, 'geral': geral, 'dados_imoveis': dados_imoveis
    })