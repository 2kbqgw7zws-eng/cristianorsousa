from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Sum, Count, Avg, Max
from django.db.models.functions import TruncMonth
from .models import Imovel, Locacao
import datetime
from django.template.loader import get_template
from xhtml2pdf import pisa  # <--- ESSA LINHA É CRUCIAL

# --- FUNÇÃO AUXILIAR ---
def buscar_dados_relatorio(ano_selecionado):
    locacoes_ano = Locacao.objects.filter(data_entrada__year=ano_selecionado)

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
    
    return {
        'ano': ano_selecionado,
        'ano_anterior': ano_selecionado - 1,
        'ano_proximo': ano_selecionado + 1,
        'geral': geral,
        'dados_imoveis': dados_imoveis
    }

# --- VIEW 1: Tela ---
def relatorio_geral(request):
    hoje = datetime.date.today()
    try:
        ano = int(request.GET.get('ano', hoje.year))
    except ValueError:
        ano = hoje.year

    contexto = buscar_dados_relatorio(ano)
    return render(request, 'relatorio.html', contexto)

# --- VIEW 2: PDF (A FUNÇÃO QUE ESTÁ FALTANDO) ---
def download_relatorio_pdf(request):
    hoje = datetime.date.today()
    try:
        ano = int(request.GET.get('ano', hoje.year))
    except ValueError:
        ano = hoje.year

    contexto = buscar_dados_relatorio(ano)
    template_path = 'relatorio_pdf.html'
    template = get_template(template_path)
    html = template.render(contexto)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Relatorio_{ano}.pdf"'

    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse('Erros ao gerar PDF <pre>' + html + '</pre>')
    return response