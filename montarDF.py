from tabulate import tabulate
import calendar
import pandas as pd
import warnings
import locale
import auxiliares
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import argparse
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configure locale and warnings
locale.setlocale(locale.LC_ALL, 'pt_BR.utf8')
warnings.simplefilter(action='ignore', category=FutureWarning)

# Constants
MENSALIDADE_VALOR = 125
FAXINA_VALOR = 45
PIX_KEY = "canteirosementesdivinas@gmail.com"
BANCO_INFO = {
    'banco': '336 - Banco C6 S.A.',
    'agencia': '0001',
    'conta': '26007876-0'
}
VALOR_PAGO_COLUMN = 'VALOR PAGO'
DOACOES = 'DOAÇÕES'
MEDIUM_CONSULTA = 'MEDIUM DE CONSULTA'
CALENDARIO_GIRAS = "Calendário de Giras 2025"

# Global variables
aux = auxiliares
sh = aux.abrir_planilha()
NOME_MES = calendar.month_name[datetime.now().month].capitalize()

# New global variables
df_mensalidades = None
df_doacoes = None
df_contas = None
df_trabalhos = None
df_agenda = None
df_valores = None
df_arrecadado = None
df_pendente = None
df_total = None

def get_mensalidades() -> None:
    """
    Obtém e exibe as mensalidades pagas e em aberto.

    Returns:
        None
    """
    global df_mensalidades
    try:
        sh = aux.abrir_planilha_dirigentes()
        logger.info('Mês de referência: %s', NOME_MES.upper())

        total_arrecadado_cell = sh.worksheet("2024").find("Total Arrecadado")
        range_dados = f'A2:Z{total_arrecadado_cell.row}'
        dados = sh.worksheet("2024").get(range_dados)

        df = pd.DataFrame(dados)
        new_header = df.iloc[0]
        df = df[1:]
        df.columns = new_header

        df = pd.concat([df['NOME'], df[NOME_MES.upper()]], axis=1, ignore_index=True)
        df.columns = ['NOME', VALOR_PAGO_COLUMN]
        df = df[df['NOME'] != DOACOES]

        # Display paid fees
        aux.montar_headers('| MENSALIDADES PAGAS |')
        adimplente = df.dropna()
        adimplente = adimplente[(df != '').all(axis=1)]
        aux.imprimir_dados('arquivo', adimplente)

        # Display unpaid fees
        aux.montar_headers('| MENSALIDADES EM ABERTO |')
        inadimplente = df[df[VALOR_PAGO_COLUMN].isna() | (df[VALOR_PAGO_COLUMN] == '')]

        nomes_inadimplentes = inadimplente['NOME'].tolist()
        string_formatada = aux.limitar_caracteres(', '.join(nomes_inadimplentes))
        logger.info(string_formatada)

        valor_em_aberto = len(inadimplente) * MENSALIDADE_VALOR
        logger.info('Valor em aberto: R$. %d', valor_em_aberto)

        df_mensalidades = df
    except Exception as e:
        logger.error("Erro ao processar mensalidades: %s", e)

def get_doacoes() -> None:
    """
    Obtém e exibe as doações do mês atual.

    Returns:
        None
    """
    global df_doacoes
    try:
        sh = aux.abrir_planilha_dirigentes()
        total_arrecadado_cell = sh.worksheet("2024").find("Total Arrecadado")
        data = sh.worksheet("2024").get(f'A2:Z{total_arrecadado_cell.row}')

        df = pd.DataFrame(data[1:], columns=data[0])
        df = df.fillna(value='0,00')

        filtro_doacao = (df['NOME'] == DOACOES) & (df[NOME_MES] != '') & (df[NOME_MES] != '0')
        doacao_mes_atual = df.loc[filtro_doacao, NOME_MES].values

        aux.montar_headers('| DOAÇÕES |')
        logger.info('DOAÇÕES %s: %s', NOME_MES, doacao_mes_atual)

        df_doacoes = df
    except Exception as e:
        logger.error("Erro ao processar doações: %s", e)

def get_contas() -> None:
    """
    Obtém e exibe as contas pagas do mês atual.

    Returns:
        None
    """
    global df_contas
    try:
        sh = aux.abrir_planilha_dirigentes()
        total_despesas_cell_inicio = sh.worksheet("2024").find("DESPESAS")
        total_despesas_cell_final = sh.worksheet("2024").find("Total Despesas")

        df = pd.DataFrame(sh.worksheet("2024").get(
            f'A{total_despesas_cell_inicio.row}:Z{total_despesas_cell_final.row}'
        ))

        new_header = df.iloc[0]
        df = df[1:]
        df.columns = new_header

        df = pd.concat([df['DESPESAS'], df[NOME_MES.upper()]],
                      ignore_index=True, axis=1, join="outer")
        df = df.replace(to_replace='None', value='NaN').dropna()
        df.columns = ['DESPESAS', VALOR_PAGO_COLUMN]

        logger.info('Mês de referência: %s', NOME_MES.upper())
        aux.montar_headers('| CONTAS PAGAS |')
        aux.imprimir_dados('arquivo', df)

        df_contas = df
    except Exception as e:
        logger.error("Erro ao processar contas: %s", e)

def get_tarefas() -> None:
    """
    Obtém e exibe as tarefas do mês atual.

    Returns:
        None
    """
    try:
        aux.montar_headers('| ATIVIDADES DO MÊS |')
        data = sh.worksheet("Rodizio de Tarefas 2025").get('A3:AA100')
        df = pd.DataFrame(data[1:], columns=data[0])

        atividades_mes_atual = []
        for index, row in df.iterrows():
            if row['ATIVIDADE'] != '':
                atividade = row['ATIVIDADE'].split('\n', 1)[0]
                atividades_mes_atual.append([atividade.strip(), row[NOME_MES.upper()]])

        df = pd.DataFrame(atividades_mes_atual, columns=['ATIVIDADE', NOME_MES.upper()])
        aux.imprimir_dados('arquivo', df)
        logger.info('Para maiores detalhes: https://t.ly/WtoHr')
    except Exception as e:
        logger.error("Erro ao processar tarefas: %s", e)

def get_faxina() -> None:
    """
    Obtém e exibe as informações de faxina do mês atual.

    Returns:
        None
    """
    try:
        filtro_faxina = datetime.now().strftime('/%m/%Y')
        aux.montar_headers('| FAXINA |')

        df = pd.DataFrame(sh.worksheet("Rodízio de Faxina").get('E:H'))
        df.columns = ['DATA', 'NOME_MES', 'TIPO', 'DataPgto']
        df = df[df['DATA'].str.contains(filtro_faxina)]
        df = df.sort_values(by='DATA', ascending=True, na_position='first')

        df['DataPgto'] = 'Data limite para pagamento: ' + df['DataPgto']
        df['mensagem'] = df['DATA'] + ' - ' + df['NOME_MES'] + ' ' + df['TIPO'] + ' - ' + df['DataPgto']

        aux.mensagem_faxina()
        logger.info("")
        logger.info("\n".join(df['mensagem']))
        aux.mensagem_pos_faxina()
    except Exception as e:
        logger.error("Erro ao processar faxina: %s", e)

def get_aniversarios() -> None:
    """
    Obtém e exibe os aniversariantes do mês atual.

    Returns:
        None
    """
    global df_aniversarios

    try:
        sh = aux.abrir_planilha_dirigentes()
        filtro_aniversario = datetime.now().strftime('/%m')

        aux.montar_headers('| ANIVERSARIANTES |')
        df_plan_mediuns = pd.DataFrame(sh.worksheet("Respostas ao formulário 1").get_all_records())

        df = pd.concat([
            df_plan_mediuns['Data de Nascimento:'].apply(str).str[:5],
            df_plan_mediuns['Nome:']
        ], axis=1, join="outer", ignore_index=True)

        df = df[df[0].str.contains(filtro_aniversario)]
        df.columns = ['DATA', 'ANIVERSARIANTE']
        df = df.sort_values(by='DATA', ascending=True, na_position='first')

        aux.imprimir_dados('arquivo', df)
        df_aniversarios = df

    except Exception as e:
        logger.error("Erro ao processar aniversários: %s", e)

def get_cambones() -> None:
    """
    Obtém e exibe os cambones do mês atual.

    Returns:
        None
    """
    try:
        df = pd.DataFrame(sh.worksheet("Cambones").get('A1:Z'))
        new_header = df.iloc[0]
        df = df[1:]
        df.columns = new_header.str.upper()

        df = pd.concat([df[MEDIUM_CONSULTA], df[NOME_MES.upper()]],
                      ignore_index=True, axis=1, join="outer")
        df.columns = [MEDIUM_CONSULTA, 'CAMBONE']

        aux.montar_headers('| CAMBONES |')
        df = df.dropna()
        aux.imprimir_dados('arquivo', df)
    except Exception as e:
        logger.error("Erro ao processar cambones: %s", e)

def get_cambones_dirigentes() -> None:
    """
    Obtém e exibe os cambones dos dirigentes do mês atual.

    Returns:
        None
    """
    try:
        df = pd.DataFrame(sh.worksheet("Cambones").get('A1:Z'))
        new_header = df.iloc[0]
        df = df[1:]
        df.columns = new_header.str.upper()

        df = pd.concat([df[MEDIUM_CONSULTA], df[NOME_MES.upper()]],
                      ignore_index=True, axis=1, join="outer")
        df.columns = [MEDIUM_CONSULTA, 'CAMBONE']

        medians_permitidos = ["Elanisia", "Paulo M.", "Luana", "Thais", "Soraia"]
        df = df[df[MEDIUM_CONSULTA].isin(medians_permitidos)]
        df = df.dropna()

        aux.montar_headers('| CAMBONES |')
        aux.imprimir_dados('arquivo', df)
    except Exception as e:
        logger.error("Erro ao processar cambones dos dirigentes: %s", e)

def get_gira_semana() -> None:
    """
    Obtém e exibe informações sobre a próxima gira.

    Returns:
        None
    """
    try:
        filtro = aux.proximo_sabado().strftime("%d/%m")
        aux.montar_headers('| GIRA ATUAL |')

        df = pd.DataFrame(sh.worksheet(CALENDARIO_GIRAS).get('A:G'))
        df = df[df[0].str.contains(filtro)]

        if df[1].iloc[0] == 'Não haverá Gira':
            output_string = (
                "Neste sábado: %s\n"
                "ATENÇÃO: %s\n"
            ) % (df['DATA'].iloc[0], df['LINHA'].iloc[0])
        else:
            output_string = (
                "Neste sábado: %s\n"
                "Linha de trabalho: %s\n"
                "Responsável(is): %s\n"
                "Grupo Faxina: %s\n"
                "Desenvolvimento: %s\n"
                "Horário de início: %s\n"
            ) % (df[0].iloc[0], df[1].iloc[0], df[2].iloc[0], df[3].iloc[0], df[4].iloc[0], df[5].iloc[0])

        logger.info(output_string)
    except Exception as e:
        logger.error("Erro ao processar gira da semana: %s", e)

def get_trabalhos_mes() -> None:
    """
    Obtém e exibe os trabalhos do mês atual.

    Returns:
        None
    """
    global df_trabalhos_mes
    try:
        filtro = aux.proximo_sabado().strftime("/%m/")
        aux.montar_headers('| CALENDARIO |')

        df = pd.DataFrame(sh.worksheet(CALENDARIO_GIRAS).get('A:C'))
        df = df[df[0].str.contains(filtro)]

        for index, row in df.iterrows():
            if "Não haverá gira" in row[1]:
                output_string = "%s - Não haverá gira" % row[0]
            else:
                output_string = "%s - %s" % (row[0], row[1])
            logger.info(output_string)

        df_trabalhos_mes = df
    except Exception as e:
        logger.error("Erro ao processar trabalhos do mês: %s", e)

def get_agenda_completa() -> None:
    """
    Obtém e exibe a agenda completa de girass e trabalhos.

    Returns:
        None
    """
    global df_agenda_completa
    try:
        hoje = datetime.now()
        mes_corrente = hoje.month
        ano_corrente = hoje.year

        aux.montar_headers('| PROXIMAS GIRAS E TRABALHOS |')
        df = pd.DataFrame(sh.worksheet(CALENDARIO_GIRAS).get('A:G'))
        df.columns = ['DATA', 'DESCRICAO', 'RESPONSAVEL', 'PORTEIRA', 'PREGIRA', 'APOIO', 'TAB. COROADOS']
        df['DATA'] = pd.to_datetime(df['DATA'], format="%d/%m/%Y", errors='coerce')

        df = df[
            (df['DATA'].dt.month == mes_corrente) &
            (df['DATA'].dt.year == ano_corrente) &
            (df['DATA'] > hoje)
        ]

        for index, row in df.iterrows():
            if "Não haverá gira" in row['DESCRICAO']:
                output_string = "%s - *Não haverá gira*" % row['DATA'].strftime('%d/%m/%Y')
            else:
                output_string = "%s - %s " % (row['DATA'].strftime('%d/%m/%Y'), row['DESCRICAO'])

            if pd.notna(row['RESPONSAVEL']):
                output_string += "Responsável: %s" % row['RESPONSAVEL']

            if pd.notna(row['PREGIRA']):
                pregira_formatado = row['PREGIRA'].replace("; ", "\n")
                output_string += "\nPré gira: %s\n" % pregira_formatado

            if pd.notna(row['TAB. COROADOS']):
                output_string += "Tab. Coroados: SIM\n"

            logger.info(output_string)

        df_agenda_completa = df
    except Exception as e:
        logger.error("Erro ao processar agenda completa: %s", e)

def mensagem_padrao() -> None:
    """
    Exibe a mensagem padrão com informações sobre pagamentos.

    Returns:
        None
    """
    mensagens = [
        '*O grupo ficará trancado até amanhã pela manhã,*',
        '*somente os dirigentes poderão enviar mensagens*',
        '*Caso tenham alguma dúvida comuniquem no particular.*\n',
        'Conforme Declaração de Ciência de Cobrança Recorrente:',
        'Data limite para pagamento da mensalidade: *Dia _15_ do mês.*\n',
        "Valor da mensalidade: R$ %d,00 (cento e vinte e cinco reais)\n" % MENSALIDADE_VALOR,
        "_Chave PIX_: *%s*\n" % PIX_KEY,
        'Dados do Pagamento: Banco: %s' % BANCO_INFO["banco"],
        'Agência: %s - Conta Corrente: %s' % (BANCO_INFO["agencia"], BANCO_INFO["conta"])
    ]
    for mensagem in mensagens:
        logger.info(mensagem)

def mensagem_faxina() -> None:
    """
    Exibe a mensagem padrão sobre faxina.

    Returns:
        None
    """
    mensagens = [
        'O Pagamento deve ser feito até 5 (cinco) dias\n'
        'antes da data marcada para realizar a faxina.\n'
        "Valor da faxina: R$ %d,00 (quarenta e cinco reais)\n" % FAXINA_VALOR,
        "_Chave PIX_: *%s*\n" % PIX_KEY,
        'Dados do Pagamento: Banco: %s' % BANCO_INFO["banco"],
        'Agência: %s - Conta Corrente: %s' % (BANCO_INFO["agencia"], BANCO_INFO["conta"])
    ]
    for mensagem in mensagens:
        logger.info(mensagem)

def mensagem_pos_faxina() -> None:
    """
    Exibe a mensagem de lembrete após a faxina.

    Returns:
        None
    """
    mensagens = [
        '\n_LEMBRETE_: Caso opte por pagar a faxina junto a mensalidade,\n'
        'deve informar nas  observações: MENSALIDADE+FAXINA DD/MM/AAAA grupo X.'
    ]
    for mensagem in mensagens:
        logger.info(mensagem)

def para_filhos() -> None:
    """
    Executa a sequência de funções para exibir informações para os filhos.

    Returns:
        None
    """
    mensagem_padrao()
    get_gira_semana()
    get_trabalhos_mes()
    get_cambones()
    get_tarefas()

def para_dirigentes() -> None:
    """
    Executa a sequência de funções para exibir informações para os dirigentes.

    Returns:
        None
    """
    get_gira_semana()
    get_agenda_completa()
    get_cambones_dirigentes()
    get_tarefas()

def get_arrecadado():
    global df_arrecadado
    try:
        logger.info("Getting arrecadado data")
        # ... existing code ...
        return df_arrecadado
    except Exception as e:
        logger.error(f"Error in get_arrecadado: {e}")
        return None

def get_pendente():
    global df_pendente
    try:
        logger.info("Getting pendente data")
        # ... existing code ...
        return df_pendente
    except Exception as e:
        logger.error(f"Error in get_pendente: {e}")
        return None

def get_total():
    global df_total
    try:
        logger.info("Getting total data")
        # ... existing code ...
        return df_total
    except Exception as e:
        logger.error(f"Error in get_total: {e}")
        return None

def run_all():
    try:
        logger.info("Running all methods")
        get_mensalidades()
        get_doacoes()
        get_contas()
        get_trabalhos_mes()
        get_agenda_completa()
        # get_valores()
        # get_arrecadado()
        # get_pendente()
        # get_total()
        logger.info("All methods completed successfully")
        return True
    except Exception as e:
        logger.error(f"Error in run_all: {e}")
        return False

def format_dataframe_for_whatsapp(df, title=None):
    if df is None or df.empty:
        return "Nenhum dado disponível."

    try:
        result = f"*{title}*\n\n" if title else ""

        for index, row in df.iterrows():
            for col in df.columns:
                value = row[col]
                if isinstance(value, (int, float)):
                    if 'valor' in col.lower() or 'total' in col.lower():
                        value = f"R$ {value:.2f}"
                    else:
                        value = str(value)
                result += f"*{col}:* {value}\n"
            result += "\n"

        return result
    except Exception as e:
        logger.error(f"Error formatting DataFrame: {e}")
        return f"Erro ao formatar dados: {str(e)}"

def print_dataframe(title, df):
    """Print a formatted dataframe with a title."""
    print(f"\n=== {title} ===")
    print(format_dataframe_for_whatsapp(df))

def execute_command(command_name, command_func):
    """Execute a command function and print its result."""
    command_func()
    print_dataframe(command_name.upper(), globals()[f"df_{command_name.lower()}"])

def setup_parser():
    """Set up and return the argument parser with all commands."""
    parser = argparse.ArgumentParser(description='Process financial data for WhatsApp bot')

    # Define command mapping
    commands = {
        'informacao': para_filhos,
        'aniversarios': get_aniversarios,
        'mensalidades': get_mensalidades,
        'doacoes': get_doacoes,
        'contas': get_contas,
        'trabalhos_mes': get_trabalhos_mes,
        'agenda_completa': get_agenda_completa,
        # 'arrecadado': get_arrecadado,
        'pendente': get_pendente,
        # 'total': get_total
    }

    # Add arguments based on commands
    for cmd in commands:
        parser.add_argument(f'--get{cmd.replace("_", "").title()}',
                           action='store_true',
                           help=f'Run get_{cmd} method')

    parser.add_argument('--all', action='store_true', help='Run all methods')

    return parser, commands

def process_commands(args, commands):
    """Process the parsed arguments and execute the appropriate commands."""
    # If no arguments provided, run all
    if not any(vars(args).values()):
        args.all = True

    if args.all:
        run_all()
        # Print all dataframes
        for cmd in commands:
            print_dataframe(cmd.upper(), globals()[f"df_{cmd}"])
    else:
        # Execute only the requested commands
        for cmd, func in commands.items():
            arg_name = f"get{cmd.replace('_', '').title()}"
            if getattr(args, arg_name, False):
                execute_command(cmd, func)

def main():
    parser, commands = setup_parser()
    args = parser.parse_args()
    process_commands(args, commands)

if __name__ == "__main__":
        # logger.info("Running all methods")
        # get_mensalidades() - OK
        # get_doacoes() - Com erro
        # get_contas() - OK
        # get_trabalhos_mes() - OK
        # get_agenda_completa() - OK
        # get_arrecadado()  -Erro
        # get_pendente()
        # get_total()
        # logger.info("All methods completed successfully")
        # para_filhos()
        main()
