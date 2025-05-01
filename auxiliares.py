from pathlib import Path
import pygments
from tabulate import tabulate
import sys
import gspread
import pandas as pd
import warnings
import locale
import os
from dotenv import load_dotenv
from pygments.formatters import ImageFormatter
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Union

# Configure locale and warnings
load_dotenv()
env_nome = os.getenv('NODE_ENV', 'DEV').upper()
if env_nome == 'PRODUCTION':
    local_arquivo_config = '/etc/secrets/credentials.json'
else:
    local_arquivo_config = 'D:\\CONFIG_BOT\\credentials.json'
print(f"Caminho do arquivo de config: {local_arquivo_config}")

locale.setlocale(locale.LC_ALL, 'pt_BR.utf8')
warnings.simplefilter(action='ignore', category=FutureWarning)
pd.set_option('display.max_colwidth', 30)
pd.set_option('display.colheader_justify', 'left')

gc = gspread.service_account(filename=local_arquivo_config)


def abrir_planilha() -> gspread.Spreadsheet:
    """
    Abre a planilha principal usando as credenciais configuradas.

    Returns:
        gspread.Spreadsheet: Objeto da planilha aberta
    """
    # gc = gspread.service_account(filename='config/credentials.json')
    sh = gc.open_by_key("16tjePCI2QMaMIOLIFVNYjcM7A2UFHYpt6DZ-sk6hioo")
    return sh

def abrir_planilha_dirigentes() -> gspread.Spreadsheet:
    """
    Abre a planilha de dirigentes usando as credenciais configuradas.

    Returns:
        gspread.Spreadsheet: Objeto da planilha aberta
    """
    sh = gc.open_by_key("10DW9L8Qp88T9xG2KhzK8I8theLHDIch_dn6LH88_dB0")
    return sh

def montar_headers(titulo: str) -> None:
    """
    Monta e exibe um cabeçalho formatado.

    Args:
        titulo (str): Título a ser exibido no cabeçalho

    Returns:
        None
    """
    tamanho = len(titulo)
    titulo = titulo.ljust(int((24 - tamanho) / 2) + tamanho, "=").rjust(24, "=")
    print('')
    print(titulo)
    print('')

def limitar_caracteres(texto: str) -> str:
    """
    Limita o número de caracteres por linha em um texto.

    Args:
        texto (str): Texto a ser formatado

    Returns:
        str: Texto formatado com quebras de linha
    """
    palavras = texto.split()
    linhas = []
    linha_atual = palavras[0]

    for palavra in palavras[1:]:
        if len(linha_atual + " " + palavra) <= 36:
            linha_atual += " " + palavra
        else:
            linhas.append(linha_atual)
            linha_atual = palavra

    linhas.append(linha_atual)
    return '\n'.join(linhas)

def imprimir_lista_formatada(lista: Dict[str, List[Any]], coluna: str) -> None:
    """
    Imprime uma lista formatada.

    Args:
        lista (Dict[str, List[Any]]): Dicionário contendo a lista a ser formatada
        coluna (str): Nome da coluna a ser exibida

    Returns:
        None
    """
    print(" : ".join(lista['columns']))
    for item in lista[coluna]:
        print(f"{item[0]}: {item[1]}")

def proximo_sabado() -> datetime:
    """
    Calcula a data do próximo sábado.

    Returns:
        datetime: Data do próximo sábado
    """
    hoje = datetime.now()
    dia_da_semana = datetime.now().weekday()
    dias_ate_sabado = (5 - dia_da_semana + 7) % 7
    proximo_sabado = hoje + timedelta(days=dias_ate_sabado)
    return proximo_sabado

def imprimir_dados(tipo_saida_tabela: str, df: pd.DataFrame) -> None:
    """
    Imprime dados em formato de tabela ou lista.

    Args:
        tipo_saida_tabela (str): Tipo de saída ('arquivo' ou 'tela')
        df (pd.DataFrame): DataFrame contendo os dados a serem exibidos

    Returns:
        None
    """
    dict_data = df.to_dict(index=False, orient='split')

    if tipo_saida_tabela == 'arquivo':
        imprimir_lista_formatada(dict_data, 'data')
    else:
        print(tabulate(df, headers='keys', tablefmt='text', stralign='left', showindex=False))

def mensagem_padrao() -> None:
    """
    Exibe a mensagem padrão com informações sobre pagamentos.

    Returns:
        None
    """
    linhas = [
        '*O grupo ficará trancado até amanhã pela manhã,*',
        '*somente os dirigentes poderão enviar mensagens*',
        '*Caso tenham alguma dúvida comuniquem no particular.*\n',
        'Conforme Declaração de Ciência de Cobrança Recorrente:',
        'Data limite para pagamento da mensalidade: *Dia _15_ do mês.*\n',
        "Valor da mensalidade: R$ 125,00 (cento e vinte e cinco reais)\n",
        "_Chave PIX_: *canteirosementesdivinas@gmail.com*\n",
        'Dados do Pagamento: Banco: 336 - Banco C6 S.A.',
        'Agência: 0001 - Conta Corrente: 26007876-0'
    ]
    for linha in linhas:
        print(linha)

def mensagem_faxina() -> None:
    """
    Exibe a mensagem padrão sobre faxina.

    Returns:
        None
    """
    linhas = [
        'O Pagamento deve ser feito até 5 (cinco) dias\n'
        'antes da data marcada para realizar a faxina.\n'
        'Valor da faxina: R$ 45,00 (quarenta e cinco reais)\n'
        "_Chave PIX_: *canteirosementesdivinas@gmail.com*\n",
        'Dados do Pagamento: Banco: 336 - Banco C6 S.A.',
        'Agência: 0001 - Conta Corrente: 26007876-0'
    ]
    for linha in linhas:
        print(linha)

def mensagem_pos_faxina() -> None:
    """
    Exibe a mensagem de lembrete após a faxina.

    Returns:
        None
    """
    linhas = [
        '\n_LEMBRETE_: Caso opte por pagar a faxina junto a mensalidade,\n'
        'deve informar nas  observações: MENSALIDADE+FAXINA DD/MM/AAAA grupo X.'
    ]
    for linha in linhas:
        print(linha)
