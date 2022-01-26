from django.test import TestCase
from controle_gastos.models import Receitas, Despesas

class ModelsTestCase(TestCase):
    def setUp(self):
        self.receita = Receitas(
            descricao = 'Receita de Teste',
            valor = 10.99,
            data = '2022-01-25'
        )

        self.despesa = Despesas(
            descricao = 'Despesa de Teste',
            valor = 10.99,
            data = '2022-01-25',
            categoria = 'O'
        )

    def test_verifica_atributos_de_uma_receita(self):
        '''
        Teste que verifica se os atributos de uma Receita estão corretos
        '''
        self.assertEqual(self.receita.descricao, 'Receita de Teste')
        self.assertEqual(self.receita.valor, 10.99)
        self.assertEqual(self.receita.data, '2022-01-25')

    def test_verifica_atributos_de_uma_despesa(self):
        '''
        Teste que verifica se os atributos de uma Despesa estão corretos
        '''
        self.assertEqual(self.despesa.descricao, 'Despesa de Teste')
        self.assertEqual(self.despesa.valor, 10.99)
        self.assertEqual(self.despesa.data, '2022-01-25')
        self.assertEqual(self.despesa.categoria, 'O')

