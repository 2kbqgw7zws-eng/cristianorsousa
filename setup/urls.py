# --- ROTAS DE ADVOCACIA ---
    # Mudamos de 'admin/advocacia/...' para 'advocacia/...'
    path('advocacia/relatorio/', advocacia_views.relatorio_advocacia, name='relatorio_advocacia'),
    path('advocacia/relatorio/pdf/', advocacia_views.download_advocacia_pdf, name='download_advocacia_pdf'),
    path('advocacia/relatorio/excel/', advocacia_views.download_advocacia_excel, name='download_advocacia_excel'),