from rest_framework import serializers
from controle_gastos.models import Receitas, Despesas

class ReceitasSerializer(serializers.ModelSerializer):
    class Meta:
        model = Receitas
        fields = ['descricao', 'valor', 'data']

class DespesasSerializer(serializers.ModelSerializer):    
    class Meta:
        model = Despesas
        fields = ['descricao', 'valor', 'data', 'categoria']

class DespesasMethodGetSerializer(serializers.ModelSerializer):
    categoria = serializers.SerializerMethodField()

    def get_categoria(self, obj):
        return obj.get_categoria_display()

    class Meta:
        model = Despesas
        fields = ['descricao', 'valor', 'data', 'categoria']

class ResumoMesSerializer(serializers.Serializer):
    total_receitas = serializers.FloatField()
    total_despesas = serializers.FloatField()
    saldo_final = serializers.FloatField()
    gastos_por_categoria = serializers.DictField()

