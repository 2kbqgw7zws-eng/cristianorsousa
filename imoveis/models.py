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
        managed = False  
        verbose_name_plural = "Visualizar Relatório Gerencial"

# A CLASSE DESPESA DEVE FICAR FORA DAS OUTRAS (NA MARGEM ESQUERDA)
class Despesa(models.Model):
    CATEGORIAS = [
        ('CONDOMINIO', 'Condomínio'),
        ('IPTU', 'IPTU'),
        ('ENERGIA', 'Energia Elétrica'),
        ('INTERNET', 'Internet'),
        ('LIMPEZA', 'Limpeza/Lavanderia'),
        ('MANUTENCAO', 'Manutenção'),
        ('OUTROS', 'Outros'),
    ]

    imovel = models.ForeignKey(Imovel, on_delete=models.CASCADE, related_name='despesas')
    categoria = models.CharField(max_length=20, choices=CATEGORIAS)
    descricao = models.CharField(max_length=200, verbose_name="Descrição")
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    data_pagamento = models.DateField(verbose_name="Data do Pagamento")

    def __str__(self):
        return f"{self.imovel.nome} - {self.get_categoria_display()} - R$ {self.valor}"

    class Meta:
        verbose_name_plural = "Despesas"
        class Imovel(models.Model):
    # ... campos existentes ...
    valor_compra = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Valor de Compra/Investimento")
    
    # Mantenha o restante do código igual