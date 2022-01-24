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
    descricao = models.CharField(max_length=120, blank=False, null=False, verbose_name='Descrição')
    valor = models.FloatField(blank=False, null=False, verbose_name='Valor')
    data = models.DateField(blank=False, null=False, verbose_name='Data')

    def __str__(self):
        return self.descricao

    class Meta:
        verbose_name = 'Despesa'
        verbose_name_plural = 'Despesas'
