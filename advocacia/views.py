def download_advocacia_pdf(request):
    if pisa is None:
        return HttpResponse("Erro: Biblioteca PDF não encontrada.")
    
    # Captura o ano da URL. Se não vier nada, usa o ano atual.
    ano = request.GET.get('ano')
    if not ano or ano == 'None':
        ano = datetime.date.today().year
    else:
        ano = int(ano)
    
    # Busca os dados filtrando rigorosamente pelo ano selecionado
    faturamentos = FaturamentoAdvocacia.objects.filter(data__year=ano).order_by('data')
    despesas = DespesaAdvocacia.objects.filter(data__year=ano).order_by('data')
    
    contexto = {
        'ano': ano,
        'faturamentos': faturamentos,
        'despesas': despesas,
        'total_f': faturamentos.aggregate(Sum('valor'))['valor__sum'] or 0,
        'total_d': despesas.aggregate(Sum('valor'))['valor__sum'] or 0,
        'data_emissao': datetime.date.today()
    }
    
    template = get_template('relatorio_advocacia_pdf.html')
    html = template.render(contexto)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Relatorio_Advocacia_{ano}.pdf"'
    pisa.CreatePDF(html, dest=response)
    return response

def download_advocacia_excel(request):
    ano = request.GET.get('ano')
    if not ano or ano == 'None':
        ano = datetime.date.today().year
    else:
        ano = int(ano)
    
    wb = openpyxl.Workbook()
    
    # Planilha de Faturamento
    ws1 = wb.active
    ws1.title = "Faturamento"
    ws1.append(['DATA', 'CLIENTE', 'VALOR'])
    for f in FaturamentoAdvocacia.objects.filter(data__year=ano).order_by('data'):
        ws1.append([f.data.strftime('%d/%m/%Y'), f.cliente, float(f.valor)])
    
    # Planilha de Despesas
    ws2 = wb.create_sheet(title="Despesas")
    ws2.append(['DATA', 'DESCRIÇÃO', 'LOCAL', 'VALOR'])
    for d in DespesaAdvocacia.objects.filter(data__year=ano).order_by('data'):
        ws2.append([d.data.strftime('%d/%m/%Y'), d.descricao, d.local, float(d.valor)])
        
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="Financeiro_Advocacia_{ano}.xlsx"'
    wb.save(response)
    return response