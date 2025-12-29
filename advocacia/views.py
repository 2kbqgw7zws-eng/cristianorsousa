from django.shortcuts import render
from django.http import HttpResponse
from .models import DespesaAdvocacia, FaturamentoAdvocacia
from django.db.models import Sum
import datetime
import openpyxl

def relatorio_advocacia(request):
    hoje = datetime.date.today()
    total_faturamento = FaturamentoAdvocacia.objects.filter(data__year=hoje.year).aggregate(Sum('valor'))['valor__sum'] or 0
    total_despesas = DespesaAdvocacia.objects.filter(data__year=hoje.year).aggregate(Sum('valor'))['valor__sum'] or 0
    contexto = {
        'ano': hoje.year,
        'faturamento': total_faturamento,
        'despesas': total_despesas,
        'lucro': total_faturamento - total_despesas,
    }
    return render(request, 'relatorio_advocacia.html', contexto)

def download_advocacia_pdf(request):
    # Por enquanto, apenas para não dar erro
    return HttpResponse("Função PDF em implementação no servidor.")

def download_advocacia_excel(request):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Advocacia"
    ws.append(['DATA', 'CLIENTE', 'VALOR'])
    for f in FaturamentoAdvocacia.objects.all():
        ws.append([f.data.strftime('%d/%m/%Y'), f.cliente, float(f.valor)])
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="Faturamento_Advocacia.xlsx"'
    wb.save(response)
    return response