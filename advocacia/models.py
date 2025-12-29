from django.db import models

class DespesaAdvocacia(models.Model):
    TIPO_CHOICES = (('C', 'Custeio'), ('I', 'Investimento'))
    data = models.DateField()
    descricao = models.CharField(max_length=200, verbose_name="Descrição")
    local = models.CharField(max_length=100, verbose_name="Local")
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    tipo = models.CharField(max_length=1, choices=TIPO_CHOICES, default='C')

    class Meta:
        verbose_name = "Despesa"
        verbose_name_plural = "Despesas"

class FaturamentoAdvocacia(models.Model):
    data = models.DateField()
    cliente = models.CharField(max_length=150)
    documento = models.CharField(max_length=20, verbose_name="CPF/CNPJ")
    valor = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = "Faturamento"
        verbose_name_plural = "Faturamentos"

class RelatorioAdvocacia(models.Model):
    class Meta:
        managed = False
        verbose_name = "Visualizar Relatório"
        verbose_name_plural = "Visualizar Relatórios"