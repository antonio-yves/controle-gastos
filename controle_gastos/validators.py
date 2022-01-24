from datetime import datetime

def valida_data(data: str) -> bool:
    """Valida a data de uma requisição

    Args:
        data (str): 2022-01-19

    Returns:
        True: Se a data corresponder ao formato yyyy-mm-dd
        False: Se a data não corresponder ao formato yyyy-mm-dd
    """
    try:
        datetime.strptime(data, '%Y-%m-%d')
        return True
    except ValueError:
        return False

def valida_campos_nulos(dados_da_requisicao):
    """Verifica quais campos encontram-se nulos

    Args:
        dados_da_requisicao (json): Armazena os dados que vieram na requisição
    """
    campos_nulos = {}
    if 'descricao' not in dados_da_requisicao:
        campos_nulos['descricao'] = 'O campo é obrigatório!'
    if 'valor' not in dados_da_requisicao:
        campos_nulos['valor'] = 'O campo é obrigatório!'
    if 'data' not in dados_da_requisicao:
        campos_nulos['data'] = 'O campo é obrigatório!'
    return (len(campos_nulos), campos_nulos)

def valida_campos_incorretos(serializer, dados_da_requisicao):
    """Valida quais campos da requisição possuem valores que não correspondem aos esperado

    Args:
        serializer (ModelSerializer): Serializer do objeto correspondente
        dados_da_requisicao (dict): Dicionário com os dados recebidos na requisição

    Returns:
        [type]: [description]
    """
    dados_incorretos = {}
    if type(serializer.data['valor']) is str:
        try:
            float(serializer.data['valor'])
        except ValueError:
            dados_incorretos['valor'] = 'O tipo de dado informado não corresponde ao tipo de dado esperado'
    if not valida_data(dados_da_requisicao['data']):
        dados_incorretos['data'] = 'A data deve estar no formato YYYY-MM-DD'
    return dados_incorretos