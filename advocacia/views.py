def download_advocacia_excel(request):
    hoje = datetime.date.today()
    ano = int(request.GET.get('ano', hoje.year)) # Filtro de ano corrigido
    
    wb = openpyxl.Workbook()
    
    # Aba 1: Faturamento
    ws1 = wb.active
    ws1.title = "Faturamento"
    ws1.append(['DATA', 'CLIENTE', 'VALOR'])
    faturamentos = FaturamentoAdvocacia.objects.filter(data__year=ano)
    for f in faturamentos:
        ws1.append([f.data.strftime('%d/%m/%Y'), f.cliente, float(f.valor)])
    
    # Aba 2: Despesas
    ws2 = wb.create_sheet(title="Despesas")
    ws2.append(['DATA', 'DESCRIÇÃO', 'LOCAL', 'VALOR'])
    despesas = DespesaAdvocacia.objects.filter(data__year=ano)
    for d in despesas:
        ws2.append([d.data.strftime('%d/%m/%Y'), d.descricao, d.local, float(d.valor)])
        
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="Financeiro_Advocacia_{ano}.xlsx"'
    wb.save(response)
    return response