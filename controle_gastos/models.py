from django.db import models

class Receitas(models.Model):
    descricao = models.CharField(max_length=120, blank=False, null=False, verbose_name='Descrição')
    valor = models.FloatField(blank=False, null=False, verbose_name='Valor')
    data = models.DateField(blank=False, null=False, verbose_name='Data')

    def __str__(self):
        return self.descricao

    class Meta:
        verbose_name = 'Receita'
        verbose_name_plural = 'Receitas'

class Despesas(models.Model):
    CATEGORIAS = (
        ('A', 'Alimentação'),
        ('S', 'Saúde'),
        ('M', 'Moradia'),
        ('T', 'Transporte'),
        ('E', 'Educação'),
        ('L', 'Lazer'),
        ('I', 'Imprevisto'),
        ('O', 'Outro')
    )
    descricao = models.CharField(max_length=120, blank=False, null=False, verbose_name='Descrição')
    valor = models.FloatField(blank=False, null=False, verbose_name='Valor')
    data = models.DateField(blank=False, null=False, verbose_name='Data')
    categoria = models.CharField(max_length=1, choices=CATEGORIAS, default='O', blank=False, null=False, verbose_name='Categoria', editable=True)

    def __str__(self):
        return self.descricao

    class Meta:
        verbose_name = 'Despesa'
        verbose_name_plural = 'Despesas'
