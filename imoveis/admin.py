from django.shortcuts import redirect # Adicione esta importação no topo do arquivo

@admin.register(RelatorioGeral)
class RelatorioGeralAdmin(admin.ModelAdmin):
    def changelist_view(self, request, extra_context=None):
        # Redireciona o usuário para a URL que definimos no urls.py
        return redirect('/relatorio/') 

    def has_add_permission(self, request): return False
    def has_delete_permission(self, request, obj=None): return False