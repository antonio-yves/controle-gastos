from django.contrib import admin
from controle_gastos.models import Receitas, Despesas

class ReceitasAdmin(admin.ModelAdmin):
    list_display = ('id', 'descricao', 'valor', 'data')
    list_display_links = ('id', 'descricao',)
    search_fields = ('descricao', 'data')
    list_per_page = 25

class DespesasAdmin(admin.ModelAdmin):
    list_display = ('id', 'descricao', 'valor', 'data')
    list_display_links = ('id', 'descricao',)
    search_fields = ('descricao', 'data')
    list_per_page = 25

admin.site.register(Receitas, ReceitasAdmin)
admin.site.register(Despesas, DespesasAdmin)
