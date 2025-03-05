from pathlib import Path
import pygments
from tabulate import tabulate
import sys
import gspread
import pandas as pd
import warnings
import locale
from pygments.formatters import ImageFormatter
from datetime import datetime, timedelta

locale.setlocale(locale.LC_ALL, 'pt_BR.utf8')
warnings.simplefilter(action='ignore', category=FutureWarning)
pd.set_option('display.max_colwidth', 30)
pd.set_option('display.colheader_justify', 'left')



def abrir_planilha():
    gc = gspread.service_account(filename='config/credentials.json')
    sh= gc.open_by_key("16tjePCI2QMaMIOLIFVNYjcM7A2UFHYpt6DZ-sk6hioo")
    return sh

def abrir_planilha_dirigentes():
    gc = gspread.service_account(filename='config/credentials.json')
    sh= gc.open_by_key("10DW9L8Qp88T9xG2KhzK8I8theLHDIch_dn6LH88_dB0")
    return sh

def montar_headers(titulo):
    tamanho = len(titulo)
    titulo = titulo.ljust(int((24 - tamanho) / 2) + tamanho, "=").rjust(24, "=")
    print('')
    print(titulo)
    print('')

def limitar_caracteres(texto):
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

def imprimir_lista_formatada(lista, coluna):
    print(" : ".join(lista['columns']))
    for item in lista[coluna]:
        print(f"{item[0]}: {item[1]}")


def proximo_sabado():
    hoje = datetime.now()
    dia_da_semana = datetime.now().weekday()
    dias_ate_sabado = (5 - dia_da_semana + 7) % 7
    proximo_sabado = hoje + timedelta(days=dias_ate_sabado)
    return proximo_sabado


def imprimir_dados(tipo_saida_tabela, df):
    dict_data = df.to_dict(index=False, orient='split')

    if tipo_saida_tabela == 'arquivo':
        imprimir_lista_formatada(dict_data, 'data')
    else:
        print(tabulate(df, headers='keys', tablefmt='text', stralign='left', showindex=False))



def mensagem_padrao():

    linhas = [
        '*O grupo ficará trancado até amanhã pela manhã,*',
        '*somente os dirigentes poderão enviar mensagens*' ,
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

def mensagem_faxina():
    linhas=[
    'O Pagamento deve ser feito até 5 (cinco) dias\n'
    'antes da data marcada para realizar a faxina.\n'
    'Valor da faxina: R$ 45,00 (quarenta e cinco reais)\n'
    "_Chave PIX_: *canteirosementesdivinas@gmail.com*\n",
    'Dados do Pagamento: Banco: 336 - Banco C6 S.A.',
    'Agência: 0001 - Conta Corrente: 26007876-0'
    ]
    for linha in linhas:
     print(linha)

def mensagem_pos_faxina():
  linhas=[
   '\n_LEMBRETE_: Caso opte por pagar a faxina junto a mensalidade,\n'
   'deve informar nas  observações: MENSALIDADE+FAXINA DD/MM/AAAA grupo X.'
  ]
  for linha in linhas:
    print(linha)