def download_advocacia_excel(request):
    hoje = datetime.date.today()
    ano = int(request.GET.get('ano', hoje.year))
    
    wb = openpyxl.Workbook()
    
    # Aba de Faturamento
    ws1 = wb.active
    ws1.title = "Faturamento"
    ws1.append(['DATA', 'CLIENTE', 'VALOR'])
    for f in FaturamentoAdvocacia.objects.filter(data__year=ano):
        ws1.append([f.data.strftime('%d/%m/%Y'), f.cliente, float(f.valor)])
    
    # Aba de Despesas
    ws2 = wb.create_sheet(title="Despesas")
    ws2.append(['DATA', 'DESCRIÇÃO', 'LOCAL', 'VALOR'])
    for d in DespesaAdvocacia.objects.filter(data__year=ano):
        ws2.append([d.data.strftime('%d/%m/%Y'), d.descricao, d.local, float(d.valor)])
        
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="Financeiro_Advocacia_{ano}.xlsx"'
    wb.save(response)
    return response