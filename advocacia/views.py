def download_advocacia_excel(request):
    hoje = datetime.date.today()
    ano = int(request.GET.get('ano', hoje.year))
    
    wb = openpyxl.Workbook()
    
    # 1. Planilha de Faturamento
    ws1 = wb.active
    ws1.title = "Faturamento"
    # Cabeçalho
    ws1.append(['DATA', 'CLIENTE', 'VALOR (R$)'])
    # Dados
    faturamentos = FaturamentoAdvocacia.objects.filter(data__year=ano).order_by('data')
    for f in faturamentos:
        ws1.append([f.data.strftime('%d/%m/%Y'), f.cliente, float(f.valor)])
    
    # 2. Planilha de Despesas
    ws2 = wb.create_sheet(title="Despesas")
    # Cabeçalho
    ws2.append(['DATA', 'DESCRIÇÃO', 'LOCAL', 'TIPO', 'VALOR (R$)'])
    # Dados
    despesas = DespesaAdvocacia.objects.filter(data__year=ano).order_by('data')
    for d in despesas:
        ws2.append([
            d.data.strftime('%d/%m/%Y'), 
            d.descricao, 
            d.local, 
            d.get_tipo_display(), 
            float(d.valor)
        ])
        
    # Formatação de resposta
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="Financeiro_Advocacia_{ano}.xlsx"'
    wb.save(response)
    return response