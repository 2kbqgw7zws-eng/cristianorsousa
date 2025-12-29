from django.db import models

class DespesaAdvocacia(models.Model):
    # ... (mantenha seus campos data, descricao, valor, etc) ...

    class Meta:
        verbose_name = "Despesa"
        verbose_name_plural = "Despesas"

class FaturamentoAdvocacia(models.Model):
    # ... (mantenha seus campos data, cliente, valor, etc) ...

    class Meta:
        verbose_name = "Faturamento"
        verbose_name_plural = "Faturamentos"

# Modelo para o botão de Relatório
class RelatorioAdvocacia(models.Model):
    class Meta:
        managed = False # Não cria tabela no banco
        verbose_name = "Visualizar Relatório"
        verbose_name_plural = "Visualizar Relatórios"