from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Sum, Count, Avg, Max
from django.db.models.functions import TruncMonth
from .models import Imovel, Locacao
import datetime
import openpyxl # <--- Nova biblioteca
from openpyxl.styles import Font, Alignment, PatternFill
from django.template.loader import get_template
from xhtml2pdf import pisa

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

# --- VIEW 2: PDF ---
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
        return HttpResponse('Erros ao gerar PDF')
    return response

# --- VIEW 3: EXCEL (NOVA) ---
def download_relatorio_excel(request):
    hoje = datetime.date.today()
    try:
        ano = int(request.GET.get('ano', hoje.year))
    except ValueError:
        ano = hoje.year

    dados = buscar_dados_relatorio(ano)
    
    # 1. Cria o Arquivo Excel
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = f"Relatorio {ano}"

    # Estilos
    bold_font = Font(bold=True)
    header_fill = PatternFill("solid", fgColor="2c3e50") # Azul escuro
    header_font = Font(bold=True, color="FFFFFF")
    money_format = 'R$ #,##0.00'

    # 2. Cabeçalho Geral
    ws['A1'] = f"RELATÓRIO CONSOLIDADO - {ano}"
    ws['A1'].font = Font(size=14, bold=True)
    ws.merge_cells('A1:D1')

    ws['A3'] = "Faturamento Total"
    ws['B3'] = "Dias Ocupados"
    ws['C3'] = "Locações"
    ws['D3'] = "Ticket Médio"
    for cell in ws[3]: cell.font = bold_font

    ws['A4'] = dados['geral']['total_faturado'] or 0
    ws['A4'].number_format = money_format
    ws['B4'] = dados['geral']['dias_ocupados']
    ws['C4'] = dados['geral']['total_locacoes']
    ws['D4'] = dados['geral']['ticket_medio'] or 0
    ws['D4'].number_format = money_format

    # 3. Detalhes por Imóvel
    current_row = 7
    for imovel in dados['dados_imoveis']:
        # Nome do Imóvel
        ws.cell(row=current_row, column=1, value=imovel['nome']).font = Font(size=12, bold=True, color="2c3e50")
        ws.cell(row=current_row, column=4, value=f"Total: R$ {imovel['faturamento_total']}").font = bold_font
        current_row += 1

        # Cabeçalho da Tabela do Imóvel
        headers = ["Mês", "Reservas", "Média Diária", "Maior Diária"]
        for col_num, header in enumerate(headers, 1):
            cell = ws.cell(row=current_row, column=col_num, value=header)
            cell.fill = header_fill
            cell.font = header_font
        current_row += 1

        # Dados mensais
        if not imovel['meses']:
            ws.cell(row=current_row, column=1, value="Sem movimentação.")
            current_row += 1
        else:
            for mes in imovel['meses']:
                ws.cell(row=current_row, column=1, value=mes['mes_ref'].strftime("%B/%Y"))
                ws.cell(row=current_row, column=2, value=mes['qtd'])
                
                c3 = ws.cell(row=current_row, column=3, value=mes['media'])
                c3.number_format = money_format
                
                c4 = ws.cell(row=current_row, column=4, value=mes['maior'])
                c4.number_format = money_format
                
                current_row += 1
        
        current_row += 2 # Espaço entre imóveis

    # Ajustar largura das colunas
    ws.column_dimensions['A'].width = 20
    ws.column_dimensions['B'].width = 15
    ws.column_dimensions['C'].width = 15
    ws.column_dimensions['D'].width = 15

    # Retornar o arquivo
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="Relatorio_Imoveis_{ano}.xlsx"'
    wb.save(response)
    return response