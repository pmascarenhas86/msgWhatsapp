from tabulate import tabulate
import calendar
import pandas as pd
import warnings
import locale
import auxiliares as aux
import logging
from datetime import datetime
import argparse

# Configurações globais
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
locale.setlocale(locale.LC_ALL, 'pt_BR.utf8')
warnings.simplefilter(action='ignore', category=FutureWarning)

MENSALIDADE_VALOR = 125
PIX_KEY = "canteirosementesdivinas@gmail.com"
BANCO_INFO = {'banco': '336 - Banco C6 S.A.', 'agencia': '0001', 'conta': '26007876-0'}
VALOR_PAGO_COLUMN = 'VALOR PAGO'
DOACOES = 'DOAÇÕES'
MEDIUM_CONSULTA = 'MEDIUM DE CONSULTA'
CALENDARIO_GIRAS = "Calendário de Giras 2025"

sh = aux.abrir_planilha()
NOME_MES = calendar.month_name[datetime.now().month].capitalize()

df_agenda_completa = df_trabalhos_mes = df_mensalidades = df_doacoes = df_contas = df_aniversarios = None

def get_mensalidades():
    global df_mensalidades
    try:
        sh = aux.abrir_planilha_dirigentes()
        dados = sh.worksheet("2024").get(f"A2:Z{sh.worksheet('2024').find('Total Arrecadado').row}")
        colunas = dados[0]
        linhas = [row[:len(colunas)] for row in dados[1:]]
        df = pd.DataFrame(linhas, columns=colunas)
        df = df[['NOME', NOME_MES.upper()]].rename(columns={NOME_MES.upper(): VALOR_PAGO_COLUMN})
        df = df[df['NOME'] != DOACOES]

        aux.montar_headers('| MENSALIDADES PAGAS |')
        aux.imprimir_dados('arquivo', df.dropna())

        aux.montar_headers('| MENSALIDADES EM ABERTO |')
        inadimplente = df[df[VALOR_PAGO_COLUMN].isna() | (df[VALOR_PAGO_COLUMN] == '')]
        logging.info(aux.limitar_caracteres(', '.join(inadimplente['NOME'].tolist())))
        logging.info(f"Valor em aberto: R$. {len(inadimplente) * MENSALIDADE_VALOR}")

        df_mensalidades = df
    except Exception as e:
        logging.error(f"Erro ao processar mensalidades: {e}")

def get_doacoes():
    global df_doacoes
    try:
        sh = aux.abrir_planilha_dirigentes()
        dados = sh.worksheet("2024").get(f"A2:Z{sh.worksheet('2024').find('Total Arrecadado').row}")
        colunas = dados[0]
        linhas = [row[:len(colunas)] for row in dados[1:]]
        df = pd.DataFrame(linhas, columns=colunas).fillna('0,00')
        doacoes = df[(df['NOME'] == DOACOES) & (df[NOME_MES] != '') & (df[NOME_MES] != '0')]
        aux.montar_headers('| DOAÇÕES |')
        logging.info(f"DOAÇÕES {NOME_MES}: {doacoes[NOME_MES].values}")
        df_doacoes = df
    except Exception as e:
        logging.error(f"Erro ao processar doações: {e}")

def get_contas():
    global df_contas
    try:
        sh = aux.abrir_planilha_dirigentes()
        inicio = sh.worksheet("2024").find("DESPESAS").row
        fim = sh.worksheet("2024").find("Total Despesas").row
        dados = sh.worksheet("2024").get(f"A{inicio}:Z{fim}")
        colunas = dados[0]
        linhas = [row[:len(colunas)] for row in dados[1:]]
        df = pd.DataFrame(linhas, columns=colunas)
        df = df[['DESPESAS', NOME_MES.upper()]].rename(columns={NOME_MES.upper(): VALOR_PAGO_COLUMN}).dropna()
        aux.montar_headers('| CONTAS PAGAS |')
        aux.imprimir_dados('arquivo', df)
        df_contas = df
    except Exception as e:
        logging.error(f"Erro ao processar contas: {e}")

def get_trabalhos_mes():
    global df_trabalhos_mes
    try:
        filtro = aux.proximo_sabado().strftime("/%m/")
        aux.montar_headers('| CALENDARIO |')
        df = pd.DataFrame(sh.worksheet(CALENDARIO_GIRAS).get('A:C'))
        df = df[df[0].str.contains(filtro)]
        for _, row in df.iterrows():
            texto = f"{row[0]} - {'Não haverá gira' if 'Não haverá gira' in row[1] else row[1]}"
            logging.info(texto)
        df_trabalhos_mes = df
    except Exception as e:
        logging.error(f"Erro ao processar trabalhos do mês: {e}")

def get_agenda_completa():
    global df_agenda_completa
    try:
        hoje = datetime.now()
        df = pd.DataFrame(sh.worksheet(CALENDARIO_GIRAS).get('A:G'), columns=['DATA', 'DESCRICAO', 'RESPONSAVEL', 'PORTEIRA', 'PREGIRA', 'APOIO', 'TAB. COROADOS'])
        df['DATA'] = pd.to_datetime(df['DATA'], format="%d/%m/%Y", errors='coerce')
        df = df[(df['DATA'].dt.month == hoje.month) & (df['DATA'].dt.year == hoje.year) & (df['DATA'] > hoje)]

        aux.montar_headers('| PRÓXIMAS GIRAS E TRABALHOS |')
        for _, row in df.iterrows():
            texto = f"{row['DATA'].strftime('%d/%m/%Y')} - {row['DESCRICAO']}"
            if pd.notna(row['RESPONSAVEL']):
                texto += f"\nResponsável: {row['RESPONSAVEL']}"
            if pd.notna(row['PREGIRA']):
                texto += f"\nPré gira: {row['PREGIRA'].replace('; ', '\n')}"
            if pd.notna(row['TAB. COROADOS']):
                texto += "\nTab. Coroados: SIM"
            logging.info(texto)
        df_agenda_completa = df
    except Exception as e:
        logging.error(f"Erro ao processar agenda completa: {e}")

def para_filhos():
    get_mensalidades()
    get_doacoes()
    get_contas()
    get_trabalhos_mes()
    get_agenda_completa()

def setup_parser():
    parser = argparse.ArgumentParser()
    comandos = {
        'mensalidades': get_mensalidades,
        'doacoes': get_doacoes,
        'contas': get_contas,
        'trabalhos': get_trabalhos_mes,
        'agenda': get_agenda_completa,
        'informacao': para_filhos,
    }
    for nome in comandos:
        parser.add_argument(f'--{nome}', action='store_true')
    return parser, comandos

def process_commands(args, comandos):
    if not any(vars(args).values()):
        para_filhos()
    else:
        for nome, func in comandos.items():
            if getattr(args, nome, False):
                func()

def main():
    parser, comandos = setup_parser()
    args = parser.parse_args()
    process_commands(args, comandos)

if __name__ == '__main__':
    main()