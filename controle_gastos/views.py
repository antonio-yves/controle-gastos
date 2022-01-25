from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import ListAPIView
from controle_gastos.serializers import ReceitasSerializer, DespesasSerializer, DespesasMethodGetSerializer, ResumoMesSerializer
from controle_gastos.models import Receitas, Despesas
from controle_gastos.validators import valida_campos_nulos, valida_campos_incorretos
from django.db import connection

class ReceitasViewSet(ModelViewSet):
    """ViewSet responsável por gerenciar os objetos do tipo Receitas

    SuperClass:
        ModelViewSet: Contêm a implementação de várias ações relacionadas a um modelo

    Actions:
        GET: Retorna uma lista com todos os objetos do tipo Receitas ordenados pela data (mais atual para o mais antigo)
        POST: Cria um novo objeto do tipo Receitas no banco de dados da aplicação
        PUT: Atualiza os campos de um objeto já existente (utiliza como argumento o ID do objeto informado na requisição)
        DELETE: Deleta um objeto do banco de dados (utiliza como argumento o ID do objeto informado na requisição)
    """

    # Query executada quando uma requisição é do tipo GET
    queryset = Receitas.objects.all().order_by('-data')

    # Classe que Serializa os dados dos objetos
    serializer_class = ReceitasSerializer

    # Métodos HTTP permitidos no ViewSet
    http_method_names = ['get', 'post', 'put', 'delete']

    def get_queryset(self):
        '''
        Sobrescreve a função get_queryset() padrão da classe. Possibilitando a pesquisa
        de Receitas a partir da descrição.
        '''

        # Define a queryset padrão da classe
        queryset = Receitas.objects.all().order_by('-data')

        # Captura os valores enviados no parâmetro da requisição
        keywords = self.request.query_params.get('descricao')

        # Verifica se há valores no keywords
        if keywords:
            # Retorna os objetos filtrados com a descrição informada
            return queryset.filter(descricao__icontains=keywords)
        # Retorna todos os objetos ordenados do mais atual para o mais antigo
        return queryset

    def create(self, request, *args, **kwargs):
        """Função responsável pela criação de um novo objeto no banco de dados.
        É executada quando a requisição é do tipo POST.

        Args:
            request (request): Contem os dados da requisição enviada pelo cliente

        Returns:
            Receita: Retorna um novo objeto do tipo Receitas caso a solicitação atenda as regras de negócio
            Erro: Quando a solicitação não atende as regras de negócio
        """

        # Armazena os dados que vieram na requisição
        dados_da_requisicao = request.data

        # Armazena a validação dos dados da requisição
        # A validação é feita pela função valida_campos_nulos que está no arquivo validators.py
        # A função retorna uma tupla (quantidade de campos nulos: int, mensagens de erro: dict)
        campos_nulos = valida_campos_nulos(dados_da_requisicao)

        # Verifica se a quantidade de campos nulos é diferente de zero
        if campos_nulos[0] != 0:
            # Retorna as mensagens de erro armazenadas na posição 1 da tupla e retorna status 400
            return Response(campos_nulos[1], status=status.HTTP_400_BAD_REQUEST)
        else:
            # Serializa os dados que vieram na requisição
            serializer = self.serializer_class(data=dados_da_requisicao)

            # Verifica se todos os campos da serialização são válidos
            if serializer.is_valid():
                # Verifica no banco de dados se já existe um objeto com a mesma descrição para o mesmo mês
                # informado na requisição
                dados_do_banco = Receitas.objects.filter(descricao=dados_da_requisicao['descricao']).filter(data__month=dados_da_requisicao['data'].split('-')[1])

                # Caso já exista retorna uma mensagem de erro informando que um objeto com a mesma descrição
                # já existe para aquele mês o status code da resposta é 400
                if len(dados_do_banco) != 0:
                    return Response({'erro': 'Já existe uma Receita com a mesma descrição para o mês informado!'}, status=status.HTTP_400_BAD_REQUEST)
                # Se a verificação for falsa
                else:
                    # Cria o objeto serializado no banco de dados
                    serializer.save()
                    # Retorna o objeto criado e um status code 201
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
            # Se os dados não forem válidos
            # A função valida_campos_incorretos que está no arquivo validators.py
            # Retorna as mensagens de erro que foram retornadas pela função e envia um status code 400
            return Response(valida_campos_incorretos(serializer, dados_da_requisicao), status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        """Função responsável pela atualização de um objeto no banco de dados.
        É executada quando a requisição é do tipo PUT.

        Args:
            request (request): Contem os dados da requisição enviada pelo cliente

        Returns:
            Receita: Retorna o objeto atualizado caso a solicitação atenda as regras de negócio
            Erro: Quando a solicitação não atende as regras de negócio
        """

        # Armazena os dados que vieram na requisição
        dados_da_requisicao = request.data

        # Armazena a validação dos dados da requisição
        # A validação é feita pela função valida_campos_nulos que está no arquivo validators.py
        # A função retorna uma tupla (quantidade de campos nulos: int, mensagens de erro: dict)
        campos_nulos = valida_campos_nulos(dados_da_requisicao)

        # Verifica se a quantidade de campos nulos é diferente de zero
        if campos_nulos[0] != 0:
            # Retorna as mensagens de erro armazenadas na posição 1 da tupla e retorna status 400
            return Response(campos_nulos[1], status=status.HTTP_400_BAD_REQUEST)
        else:
            # Recupera a instância que vai ser atualiza (utiliza o id que vêm na requisição)
            instance = self.get_object()
            # Serializa o objeto com os novos dados
            serializer = self.get_serializer(instance, data=dados_da_requisicao)

            # Verifica se todos os campos da serialização são válidos
            if serializer.is_valid():
                # Verifica no banco de dados se já existe um objeto com a mesma descrição para o mês
                # informado na requisição
                dados_do_banco = Receitas.objects.filter(descricao=dados_da_requisicao['descricao']).filter(data__month=dados_da_requisicao['data'].split('-')[1]).exclude(id=instance.id)

                # Caso já exista retorna uma mensagem de erro informando que um objeto com a mesma descrição
                # já existe para aquele mês o status code da resposta é 400
                if len(dados_do_banco) != 0:
                    return Response({'erro': 'Já existe uma Receita com a mesma descrição para o mês informado!'}, status=status.HTTP_400_BAD_REQUEST)
                # Se a verificação for falsa
                else:
                    # Atualiza os campos do objeto e salva as alterações no banco de dados
                    self.perform_update(serializer)
                    # Retorna o objeto atualizado e um status code 200
                    return Response(serializer.data, status=status.HTTP_200_OK)
            # Se os dados não forem válidos
            # A função valida_campos_incorretos que está no arquivo validators.py
            # Retorna as mensagens de erro que foram retornadas pela função e envia um status code 400
            return Response(valida_campos_incorretos(serializer, dados_da_requisicao), status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        """Função responsável pela exclusão de um objeto no banco de dados.
        É executada quando a requisição é do tipo DELETE

        Args:
            request (request): Contem os dados da requisição enviados pelo cliente

        Returns:
            Str: Mensagem de sucesso quando o objeto é excluído
        """

        # Recupera a instância que será excluída
        instance = self.get_object()
        # Exclui a instância do banco de dados
        instance.delete()
        # Retorna uma mensagem de sucesso e um status code 200
        return Response({'detail': 'Receita excluída com sucesso!'}, status=status.HTTP_200_OK)

class DespesasViewSet(ModelViewSet):
    """ViewSet responsável por gerenciar os objetos do tipo Despesas

    SuperClass:
        ModelViewSet: Contêm a implementação de várias ações relacionadas a um modelo

    Actions:
        GET: Retorna uma lista com todos os objetos do tipo Despesas ordenados pela data (mais atual para o mais antigo)
        POST: Cria um novo objeto do tipo Despesas no banco de dados da aplicação
        PUT: Atualiza os campos de um objeto já existente (utiliza como argumento o ID do objeto informado na requisição)
        DELETE: Deleta um objeto do banco de dados (utiliza como argumento o ID do objeto informado na requisição)
    """

    # Query executada quando uma requisição é do tipo GET
    queryset = Despesas.objects.all().order_by('-data')

    # Classe que Serializa os dados dos objetos
    serializer_class = DespesasSerializer

    # Métodos HTTP permitidos no ViewSet
    http_method_names = ['get', 'post', 'put', 'delete']

    def get_queryset(self):
        '''
        Sobrescreve a função get_queryset() padrão da classe. Possibilitando a pesquisa
        de Despesas a partir da descrição.
        '''

        # Define a queryset padrão da classe
        queryset = Despesas.objects.all().order_by('-data')

        # Captura os valores enviados no parâmetro da requisição
        keywords = self.request.query_params.get('descricao')

        # Verifica se há valores no keywords
        if keywords:
            # Retorna os objetos filtrados com a descrição informada
            return queryset.filter(descricao__icontains=keywords)
        # Retorna todos os objetos ordenados do mais atual para o mais antigo
        return queryset

    def get_serializer_class(self):
        """Função que retorna a classe serializadora

        Returns:
            DespesasMethodGetSerializer: Quando a solicitação é do tipo GET
            DespesasSerializer: Para os demais tipos de solicitação
        """

        # Verifica se o método da requisição é GET
        if self.request.method == 'GET':
            # Retorna a classe serializadora correspondente
            return DespesasMethodGetSerializer
        # Retorna a classe serializadora para os demais métodos
        return DespesasSerializer

    def create(self, request, *args, **kwargs):
        """Função responsável pela criação de um novo objeto no banco de dados.
        É executada quando a requisição é do tipo POST.

        Args:
            request (request): Contem os dados da requisição enviada pelo cliente

        Returns:
            Despesa: Retorna um novo objeto do tipo Despesas caso a solicitação atenda as regras de negócio
            Erro: Quando a solicitação não atende as regras de negócio
        """

        # Armazena os dados que vieram na requisição
        dados_da_requisicao = request.data

        # Armazena a validação dos dados da requisição
        # A validação é feita pela função valida_campos_nulos que está no arquivo validators.py
        # A função retorna uma tupla (quantidade de campos nulos: int, mensagens de erro: dict)
        campos_nulos = valida_campos_nulos(dados_da_requisicao)

        # Verifica se a quantidade de campos nulos é diferente de zero
        if campos_nulos[0] != 0:
            # Retorna as mensagens de erro armazenadas na posição 1 da tupla e retorna status 400
            return Response(campos_nulos[1], status=status.HTTP_400_BAD_REQUEST)
        else:
            # Serializa os dados que vieram na requisição
            serializer = self.serializer_class(data=dados_da_requisicao)

            # Verifica se todos os campos da serialização são válidos
            if serializer.is_valid():
                # Verifica no banco de dados se já existe um objeto com a mesma descrição para o mesmo mês
                # informado na requisição
                dados_do_banco = Despesas.objects.filter(descricao__iexact=dados_da_requisicao['descricao']).filter(data__month=dados_da_requisicao['data'].split('-')[1])

                # Caso já exista retorna uma mensagem de erro informando que um objeto com a mesma descrição
                # já existe para aquele mês o status code da resposta é 400
                if len(dados_do_banco) != 0:
                    return Response({'erro': 'Já existe uma Despesa com a mesma descrição para o mês informado!'}, status=status.HTTP_400_BAD_REQUEST)
                # Se a verificação for falsa
                else:
                    # Cria o objeto serializado no banco de dados
                    serializer.save()
                    print(serializer.data)
                    # Retorna o objeto criado e um status code 201
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
            # Se os dados não forem válidos
            # A função valida_campos_incorretos que está no arquivo validators.py
            # Retorna as mensagens de erro que foram retornadas pela função e envia um status code 400
            return Response(valida_campos_incorretos(serializer, dados_da_requisicao), status=status.HTTP_400_BAD_REQUEST)
    
    def update(self, request, *args, **kwargs):
        """Função responsável pela atualização de um objeto no banco de dados.
        É executada quando a requisição é do tipo PUT.

        Args:
            request (request): Contem os dados da requisição enviada pelo cliente

        Returns:
            Receita: Retorna o objeto atualizado caso a solicitação atenda as regras de negócio
            Erro: Quando a solicitação não atende as regras de negócio
        """

        # Armazena os dados que vieram na requisição
        dados_da_requisicao = request.data

        # Armazena a validação dos dados da requisição
        # A validação é feita pela função valida_campos_nulos que está no arquivo validators.py
        # A função retorna uma tupla (quantidade de campos nulos: int, mensagens de erro: dict)
        campos_nulos = valida_campos_nulos(dados_da_requisicao)

        # Verifica se a quantidade de campos nulos é diferente de zero
        if campos_nulos[0] != 0:
            # Retorna as mensagens de erro armazenadas na posição 1 da tupla e retorna status 400
            return Response(campos_nulos[1], status=status.HTTP_400_BAD_REQUEST)
        else:
            # Recupera a instância que vai ser atualiza (utiliza o id que vêm na requisição)
            instance = self.get_object()
            # Serializa o objeto com os novos dados
            serializer = self.get_serializer(instance, data=dados_da_requisicao)

            # Verifica se todos os campos da serialização são válidos
            if serializer.is_valid():
                # Verifica no banco de dados se já existe um objeto com a mesma descrição para o mês
                # informado na requisição
                dados_do_banco = Despesas.objects.filter(descricao__iexact=dados_da_requisicao['descricao']).filter(data__month=dados_da_requisicao['data'].split('-')[1]).exclude(id=instance.id)

                # Caso já exista retorna uma mensagem de erro informando que um objeto com a mesma descrição
                # já existe para aquele mês o status code da resposta é 400
                if len(dados_do_banco) != 0:
                    return Response({'erro': 'Já existe uma Despesa com a mesma descrição para o mês informado!'}, status=status.HTTP_400_BAD_REQUEST)
                # Se a verificação for falsa
                else:
                    # Atualiza os campos do objeto e salva as alterações no banco de dados
                    self.perform_update(serializer)
                    # Retorna o objeto atualizado e um status code 200
                    return Response(serializer.data, status=status.HTTP_200_OK)
            # Se os dados não forem válidos
            # A função valida_campos_incorretos que está no arquivo validators.py
            # Retorna as mensagens de erro que foram retornadas pela função e envia um status code 400
            return Response(valida_campos_incorretos(serializer, dados_da_requisicao), status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        """Função responsável pela exclusão de um objeto no banco de dados.
        É executada quando a requisição é do tipo DELETE

        Args:
            request (request): Contem os dados da requisição enviados pelo cliente

        Returns:
            Str: Mensagem de sucesso quando o objeto é excluído
        """

        # Recupera a instância que será excluída
        instance = self.get_object()
        # Exclui a instância do banco de dados
        instance.delete()
        # Retorna uma mensagem de sucesso e um status code 200
        return Response({'detail': 'Despesa excluída com sucesso!'}, status=status.HTTP_200_OK)

class ReceitasPorMes(ListAPIView):
    """Realiza a listagem das Receitas em um mês específico.

    SuperClass:
        ListAPIView: Contêm a implementação básica para realizar a listagem de objetos

    Actions:
        GET: Retorna uma lista com os objetos do tipo Receitas em um mês específico ordenados pela data (mais atual para o mais antigo)
    """
    
    def get_queryset(self):
        '''
        Sobrescreve a função get_queryset() padrão da classe. Possibilitando filtrar as Receitas
        criadas no período informado na URL.
        '''

        # Realiza a filtragem das Receitas utilizando os parâmetros informandos na URL
        queryset = Receitas.objects.filter(
            data__month=self.kwargs['mes'], 
            data__year=self.kwargs['ano']).order_by('-data')

        # Retorna o resultado do filtro
        return queryset

    # Classe que Serializa os dados dos objetos
    serializer_class = ReceitasSerializer

class DespesasPorMes(ListAPIView):
    """Realiza a listagem das Despesas em um mês específico.

    SuperClass:
        ListAPIView: Contêm a implementação básica para realizar a listagem de objetos

    Actions:
        GET: Retorna uma lista com os objetos do tipo Despesas em um mês específico ordenados pela data (mais atual para o mais antigo)
    """
    
    def get_queryset(self):
        '''
        Sobrescreve a função get_queryset() padrão da classe. Possibilitando filtrar as Despesas
        criadas no período informado na URL.
        '''

        # Realiza a filtragem das Despesas utilizando os parâmetros informandos na URL
        queryset = Despesas.objects.filter(
            data__month=self.kwargs['mes'],
            data__year=self.kwargs['ano']).order_by('-data')

        # Retorna o resultado do filtro
        return queryset

    # Classe que Serializa os dados dos objetos
    serializer_class = DespesasMethodGetSerializer

class ResumoMes(ListAPIView):
    """Exibe o resumo de um mês específico.

    SuperClass:
        ListAPIView: Contêm a implementação básica para realizar a listagem de objetos

    Actions:
        GET: Retorna um objeto JSON com o resumo do mês informado nos parâmetros da URL
    """
    
    def get(self, request, *args, **kwargs):
        '''
        Sobrescreve a função get() padrão da classe. Possibilitando criar o resumo de acordo com
        a regra de negócio estabelecida na especificação do projeto.
        '''

        # Cria um cursor para realizar as consultas no banco de dados
        cursor = connection.cursor()

        # Executa o SELECT que realiza a soma dos valores para as Receitas do mês e ano
        # Especificados na URL
        cursor.execute(f'''
            SELECT SUM(VALOR) FROM CONTROLE_GASTOS_RECEITAS WHERE TO_CHAR(DATA, 'MM/YYYY') = '{self.kwargs['mes']}/{self.kwargs['ano']}'
        ''')
        # Armazena o resultado do SELECT na variável
        total_receitas = cursor.fetchone()

        # Executa o SELECT que realiza a soma dos valores para as Despesas do mês e ano
        # Especificados na URL
        cursor.execute(f'''
            SELECT SUM(VALOR) FROM CONTROLE_GASTOS_DESPESAS WHERE TO_CHAR(DATA, 'MM/YYYY') = '{self.kwargs['mes']}/{self.kwargs['ano']}'
        ''')
        # Armazena o resultado do SELECT na variável
        total_despesas = cursor.fetchone()

        # Verifica se os valores de Receitas e Despesas são nulos
        if not total_receitas[0] and not total_despesas[0]:
            # Retorna uma mensagem informando que não há dados para o período especificado
            return Response({'detail': 'Não foram encontrados valores para o período informado!'}, status=status.HTTP_400_BAD_REQUEST)

        # Verifica se o valor das Receitas não é nulo e se o valor para as Despesas é nulo
        if total_receitas[0] and not total_despesas[0]:
            # O Saldo Final será igual ao valor das Receitas
            saldo_final = total_receitas[0]

        # Verifica se o valor das Receitas é nulo e se o valor para as Despesas não é nulo
        if not total_receitas[0] and total_despesas[0]:
            # O Saldo Final será igual ao valor das Despesas
            saldo_final = total_despesas[0]

        # Verifica se os valores das Receitas e Despesas não são nulos
        if total_receitas[0] and total_despesas[0]:
            # O Saldo Final será as Receitas menos as Despesas
            saldo_final = total_receitas[0] - total_despesas[0]

        # Armazenará os gastos de acordo com cada categoria
        gastos_por_categoria = {}

        # Realiza o SELECT para as categorias das Despesas e armazena os resultados
        # No dicionário gastos_por_categoria
        for categoria in ['A', 'S', 'M', 'T', 'E', 'L', 'I', 'O']:
            # Executa o SELECT
            cursor.execute(f'''
                SELECT SUM(VALOR) 
                    FROM CONTROLE_GASTOS_DESPESAS 
                WHERE 
                    CATEGORIA = '{categoria}' AND 
                    TO_CHAR(DATA, 'MM/YYYY') = '{self.kwargs['mes']}/{self.kwargs['ano']}'
            ''')
            # Armazena o resultado na chave correspondente a categoria
            gastos_por_categoria[categoria] = cursor.fetchone()[0]

        # Fecha o cursor que realizou as operações no banco de dados
        cursor.close()

        # Monta o dicionário com os dados extraídos do banco de dados
        data_response = {'total_receitas': 0 if total_receitas[0] == None else total_receitas[0], 
            'total_despesas': 0 if total_despesas[0] == None else total_despesas[0], 
            'saldo_final': saldo_final, 
            'gastos_por_categoria': {
                'Alimentação': 0 if gastos_por_categoria['A'] == None else round(gastos_por_categoria['A'], 2),
                'Saúde': 0 if gastos_por_categoria['S'] == None else round(gastos_por_categoria['S'], 2),
                'Moradia': 0 if gastos_por_categoria['M'] == None else round(gastos_por_categoria['M'], 2),
                'Transporte': 0 if gastos_por_categoria['T'] == None else round(gastos_por_categoria['T'], 2),
                'Educação': 0 if gastos_por_categoria['E'] == None else round(gastos_por_categoria['E'], 2),
                'Lazer': 0 if gastos_por_categoria['L'] == None else round(gastos_por_categoria['L'], 2),
                'Imprevisto': 0 if gastos_por_categoria['I'] == None else round(gastos_por_categoria['I'], 2),
                'Outro': 0 if gastos_por_categoria['O'] == None else round(gastos_por_categoria['O'], 2),
            }}

        # Retorna o objeto JSON com os dados do Resumo e um status code 200
        return Response(data_response, status=status.HTTP_200_OK)

    # Classe que Serializa os dados dos objetos
    serializer_class = ResumoMesSerializer
