from django.shortcuts import render
from django.http import HttpResponse
from .models import DespesaAdvocacia, FaturamentoAdvocacia
from django.db.models import Sum
from django.template.loader import get_template
import datetime
import openpyxl

# Tenta importar o pisa para o PDF (essencial para o PythonAnywhere)
try:
    from xhtml2pdf import pisa
except ImportError:
    pisa = None

def relatorio_advocacia(request):
    """Exibe a página do relatório no navegador com navegação por anos"""
    hoje = datetime.date.today()
    ano_selecionado = int(request.GET.get('ano', hoje.year))
    
    # Busca os dados filtrados pelo ano
    faturamento_qs = FaturamentoAdvocacia.objects.filter(data__year=ano_selecionado)
    despesas_qs = DespesaAdvocacia.objects.filter(data__year=ano_selecionado)
    
    total_faturamento = faturamento_qs.aggregate(Sum('valor'))['valor__sum'] or 0
    total_despesas = despesas_qs.aggregate(Sum('valor'))['valor__sum'] or 0
    
    contexto = {
        'ano': ano_selecionado,
        'ano_anterior': ano_selecionado - 1,
        'ano_proximo': ano_selecionado + 1,
        'faturamento': total_faturamento,
        'despesas': total_despesas,
        'lucro': total_faturamento - total_despesas,
    }
    return render(request, 'relatorio_advocacia.html', contexto)

def download_advocacia_pdf(request):
    """Gera o arquivo PDF com a listagem detalhada"""
    if pisa is None:
        return HttpResponse("Erro: Biblioteca xhtml2pdf não encontrada no servidor.")
    
    hoje = datetime.date.today()
    ano = int(request.GET.get('ano', hoje.year))
    
    # Filtra os dados para o PDF não vir vazio
    faturamentos = FaturamentoAdvocacia.objects.filter(data__year=ano).order_by('data')
    despesas = DespesaAdvocacia.objects.filter(data__year=ano).order_by('data')
    
    contexto = {
        'ano': ano,
        'faturamentos': faturamentos,
        'despesas': despesas,
        'total_f': faturamentos.aggregate(Sum('valor'))['valor__sum'] or 0,
        'total_d': despesas.aggregate(Sum('valor'))['valor__sum'] or 0,
        'data_emissao': hoje
    }
    
    template = get_template('relatorio_advocacia_pdf.html')
    html = template.render(contexto)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Relatorio_Advocacia_{ano}.pdf"'
    
    pisa.CreatePDF(html, dest=response)
    return response

def download_advocacia_excel(request):
    """Gera o Excel com abas separadas para Faturamento e Despesas"""
    hoje = datetime.date.today()
    ano = int(request.GET.get('ano', hoje.year))
    
    wb = openpyxl.Workbook()
    
    # --- Aba 1: Faturamento ---
    ws1 = wb.active
    ws1.title = "Faturamento"
    ws1.append(['DATA', 'CLIENTE', 'VALOR'])
    faturamentos = FaturamentoAdvocacia.objects.filter(data__year=ano).order_by('data')
    for f in faturamentos:
        ws1.append([f.data.strftime('%d/%m/%Y'), f.cliente, float(f.valor)])
    
    # --- Aba 2: Despesas ---
    ws2 = wb.create_sheet(title="Despesas")
    ws2.append(['DATA', 'DESCRIÇÃO', 'LOCAL', 'VALOR'])
    despesas = DespesaAdvocacia.objects.filter(data__year=ano).order_by('data')
    for d in despesas:
        ws2.append([d.data.strftime('%d/%m/%Y'), d.descricao, d.local, float(d.valor)])
        
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="Financeiro_Advocacia_{ano}.xlsx"'
    wb.save(response)
    return response