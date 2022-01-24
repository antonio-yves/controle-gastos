from rest_framework.serializers import ModelSerializer
from controle_gastos.models import Receitas, Despesas

class ReceitasSerializer(ModelSerializer):
    class Meta:
        model = Receitas
        fields = ['descricao', 'valor', 'data']

class DespesasSerializer(ModelSerializer):
    class Meta:
        model = Despesas
        fields = ['descricao', 'valor', 'data']
