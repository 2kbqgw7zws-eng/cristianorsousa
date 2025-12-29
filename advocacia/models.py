from django.db import models

class DespesaAdvocacia(models.Model):
    data = models.DateField()
    descricao = models.CharField(max_length=255)
    local = models.CharField(max_length=255)
    valor = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.data} - {self.descricao}"

class FaturamentoAdvocacia(models.Model):
    data = models.DateField()
    cliente = models.CharField(max_length=255)
    valor = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.cliente} - R$ {self.valor}"

class ProcessoFaturamento(models.Model):
    STATUS_CHOICES = [
        ('ativo', 'Ativo'),
        ('baixado', 'Baixado'),
    ]
    
    faturamento = models.ForeignKey(FaturamentoAdvocacia, on_delete=models.CASCADE, related_name='processos')
    numero_processo = models.CharField("Processo", max_length=100)
    competencia = models.CharField("Competência", max_length=100)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='ativo')

    def __str__(self):
        return self.numero_processo

class RelatorioAdvocacia(models.Model):
    class Meta:
        managed = False
        verbose_name = "Visualizar Relatório"
        verbose_name_plural = "Visualizar Relatórios"