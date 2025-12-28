from django.db import models

class Imovel(models.Model):
    STATUS_CHOICES = (
        ('D', 'Disponível'),
        ('L', 'Alugado'),
        ('M', 'Manutenção/Limpeza'),
    )

    nome = models.CharField(max_length=100)
    endereco = models.TextField()
    descricao = models.TextField(blank=True, null=True)
    valor_diaria = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='D')
    
    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Imóvel"
        verbose_name_plural = "Imóveis"

class Locacao(models.Model):
    imovel = models.ForeignKey(Imovel, on_delete=models.CASCADE)
    cliente = models.CharField(max_length=100)
    
    # NOVOS CAMPOS
    cpf = models.CharField(max_length=14, default='000.000.000-00') 
    telefone = models.CharField(max_length=20, default='(00) 00000-0000')

    data_entrada = models.DateField()
    data_saida = models.DateField()
    valor_cobrado_diaria = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.cliente} - {self.imovel.nome}"

    class Meta:
        verbose_name = "Locação"
        verbose_name_plural = "Locações"

class RelatorioGeral(models.Model):
    class Meta:
        managed = False  # Não cria tabela no banco
        verbose_name_plural = "Visualizar Relatório Gerencial" # O nome que aparece no botão