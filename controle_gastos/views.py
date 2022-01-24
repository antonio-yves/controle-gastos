from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from controle_gastos.serializers import ReceitasSerializer, DespesasSerializer
from controle_gastos.models import Receitas, Despesas
from controle_gastos.validators import valida_campos_nulos, valida_campos_incorretos

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
