from tabulate import tabulate
import calendar
import pandas as pd
import warnings
import locale
import auxiliares
from datetime import datetime, timedelta
locale.setlocale(locale.LC_ALL, 'pt_BR.utf8')
warnings.simplefilter(action='ignore', category=FutureWarning)

#Definindo Variaveis
aux = auxiliares
sh=aux.abrir_planilha()
NOME_MES = calendar.month_name[datetime.now().month].capitalize()

def get_mensalidades():
    """
    Obtém as mensalidades pagas e em aberto, formatando e exibindo os dados.
    """
    try:
        sh = aux.abrir_planilha_dirigentes()
        print('\nMês de referência:', NOME_MES.upper())
        total_arrecadado_cell = sh.worksheet("2024").find("Total Arrecadado")
        range_dados = f'A2:Z{total_arrecadado_cell.row}'
        dados = sh.worksheet("2024").get(range_dados)
        df = pd.DataFrame(dados)
        new_header = df.iloc[0]
        df = df[1:]
        df.columns = new_header
        df = pd.concat([df['NOME'], df[NOME_MES.upper()]], axis=1, ignore_index=True)
        df.columns = ['NOME', 'VALOR PAGO']
        df = df[df['NOME'] != 'DOAÇÕES']
        aux.montar_headers('| MENSALIDADES PAGAS |')
        adimplente = df.dropna()
        adimplente = adimplente[(df != '').all(axis=1)]
        # print(adimplente)
        aux.imprimir_dados('arquivo', adimplente)
        aux.montar_headers('| MENSALIDADES EM ABERTO |')
        inadimplente = df[df['VALOR PAGO'].isna() | (df['VALOR PAGO'] == '')]

        nomes_inadimplentes = inadimplente['NOME'].tolist()
        string_formatada = aux.limitar_caracteres(', '.join(nomes_inadimplentes))
        print(string_formatada)
        valor_em_aberto = len(inadimplente) * 125
        print('Valor em aberto: R$.', valor_em_aberto)
    except Exception as e:
        print(f"Erro ao processar mensalidades: {e}")


def get_doacoes():
  sh=aux.abrir_planilha_dirigentes()
  total_arrecadado_cell = sh.worksheet("2024").find("Total Arrecadado")
  data = sh.worksheet("2024").get('A2:Z' + str(total_arrecadado_cell.row))
  df = pd.DataFrame(data[1:], columns=data[0])
  df= df.fillna(value='0,00')
  NOME_MES = datetime.now().strftime('%B').upper()  # Obtém o nome do mês atual em maiúsculas
  filtro_doacao = (df['NOME'] == 'DOAÇÕES') & (df[NOME_MES] != '') & (df[NOME_MES] != '0')
  doacao_mes_atual = df.loc[filtro_doacao, NOME_MES].values
  df_doacoes = df[df['NOME'] == 'DOAÇÕES'][[NOME_MES.upper()]]
  doacao_mes_atual_str = f'DOAÇÕES {NOME_MES}: {doacao_mes_atual}'
  aux.montar_headers('| DOAÇÕES |')

  print(doacao_mes_atual_str)


def get_contas():
  sh=aux.abrir_planilha_dirigentes()
  total_despesas_cell_inicio = sh.worksheet("2024").find("DESPESAS")
  total_despesas_cell_final = sh.worksheet("2024").find("Total Despesas")
  df = pd.DataFrame(sh.worksheet("2024").get(f'A{total_despesas_cell_inicio.row}:Z{total_despesas_cell_final.row}'))
  new_header = df.iloc[0]
  df = df[1:]
  df.columns = new_header
  df = pd.concat([df['DESPESAS'], df[NOME_MES.upper()]], ignore_index=True, axis=1, join="outer")
  df = df.replace(to_replace='None', value='NaN').dropna()
  df.columns = ['DESPESAS', 'VALOR PAGO']
  # CONTAS PAGAS
  print('\nMês de referência: ', NOME_MES.upper())
  aux.montar_headers('| CONTAS PAGAS |')
  aux.imprimir_dados('arquivo', df)

def get_tarefas():
  aux.montar_headers('| ATIVIDADES DO MÊS |')
  data = sh.worksheet("Rodizio de Tarefas 2025").get('A3:AA100')
  df = pd.DataFrame(data[1:], columns=data[0])
  # df_tarefas = df[['ATIVIDADE']]
  # df_mes_atual = df[['ATIVIDADE', NOME_MES.upper()]]
  atividades_mes_atual = []
  for index, row in df.iterrows():
      if row['ATIVIDADE'] != '':
          atividade = row['ATIVIDADE'].split('\n', 1)[0]
          atividades_mes_atual.append([atividade.strip(), row[NOME_MES.upper()]])
  df = pd.DataFrame(atividades_mes_atual, columns=['ATIVIDADE', NOME_MES.upper()])
  aux.imprimir_dados('arquivo', df)
  print('Para maiores detalhes: https://t.ly/WtoHr')

def get_faxina():
    FILTRO_FAXINA = datetime.now().strftime('/%m/%Y')
    aux.montar_headers('| FAXINA |')
    df = pd.DataFrame(sh.worksheet("Rodízio de Faxina").get('E:H'))
    df.columns = ['DATA', 'NOME_MES', 'TIPO', 'DataPgto']
    df = df[df['DATA'].str.contains(FILTRO_FAXINA)]
    df = df.sort_values(by='DATA', ascending=True, na_position='first')
    df['DataPgto'] = 'Data limite para pagamento: ' + df['DataPgto']
    df['mensagem'] = df['DATA'] + ' - ' + df['NOME_MES'] + ' ' + df['TIPO'] + ' - ' + df['DataPgto']
    aux.mensagem_faxina()
    print()
    print("\n".join(df['mensagem']))
    aux.mensagem_pos_faxina()


def get_aniversarios():
  sh=aux.abrir_planilha_dirigentes()
  FILTRO_ANIVERSARIO= datetime.now().strftime('/%m')
  aux.montar_headers('| ANIVERSARIANTES |')
  df_plan_mediuns = pd.DataFrame(sh.worksheet("Respostas ao formulário 1").get_all_records())
  df=pd.concat([df_plan_mediuns['Data de Nascimento:'].apply(str).str[:5],df_plan_mediuns['Nome:']],axis=1,join="outer",ignore_index=True)
  df=df[df[0].str.contains(FILTRO_ANIVERSARIO)]
  df.columns=['DATA','ANIVERSARIANTE']
  df=df.sort_values(by='DATA', ascending=True, na_position='first')
  aux.imprimir_dados('arquivo', df)

def get_cambones():
    df = pd.DataFrame(sh.worksheet("Cambones").get('A1:Z'))
    new_header = df.iloc[0]
    df = df[1:]
    df.columns = new_header.str.upper()
    df = pd.concat([df['MEDIUM DE CONSULTA'], df[NOME_MES.upper()]], ignore_index=True, axis=1, join="outer")
    df.columns = ['MEDIUM DE CONSULTA', 'CAMBONE']
    aux.montar_headers('| CAMBONES |')
    df = df.dropna()
    aux.imprimir_dados('arquivo', df)

def get_cambones_dirigentes():
    df = pd.DataFrame(sh.worksheet("Cambones").get('A1:Z'))
    new_header = df.iloc[0]
    df = df[1:]
    df.columns = new_header.str.upper()
    df = pd.concat([df['MEDIUM DE CONSULTA'], df[NOME_MES.upper()]], ignore_index=True, axis=1, join="outer")
    df.columns = ['MEDIUM DE CONSULTA', 'CAMBONE']
    medians_permitidos = ["Elanisia", "Paulo M.", "Luana", "Thais", "Soraia"]
    df = df[df['MEDIUM DE CONSULTA'].isin(medians_permitidos)]
    df = df.dropna()

    # Exibe o cabeçalho e imprime os dados formatados
    aux.montar_headers('| CAMBONES |')
    aux.imprimir_dados('arquivo', df)


def get_gira_semana():
  FILTRO= aux.proximo_sabado().strftime("%d/%m")
  aux.montar_headers('| GIRA ATUAL |')
  df = pd.DataFrame(sh.worksheet("Calendário de Giras 2025").get('A:G'))
  # print(df)
  df=df[df[0].str.contains(FILTRO)]
  # df.columns=['DATA','LINHA','RESPONSAVEL','FAXINA','PRE_GIRA','APOIO','ASSISTENCIA','FAXINA']
  if df[1].iloc[0]=='Não haverá Gira':
     output_string = f"Neste sábado: {df['DATA'].iloc[0]}\n" \
     f"ATENÇÃO: {df['LINHA'].iloc[0]}\n" \

  else:
      output_string = f"Neste sábado: {df[0].iloc[0]}\n" \
      f"Linha de trabalho: {df[1].iloc[0]}\n" \
      f"Responsável(is): {df[2].iloc[0]}\n" \
      f"Grupo Faxina: {df[3].iloc[0]}\n" \
      f"Desenvolvimento: {df[4].iloc[0]}\n" \
      f"Horário de início: {df[5].iloc[0]}\n" \

  print(output_string)
  # imprimir_dados('tela', df)

def get_valores():
  sh=aux.abrir_planilha_dirigentes()
  Doacoes = sh.worksheet("2024").find("DOAÇÕES")
  data = sh.worksheet("2024").get_all_values()
  df = pd.DataFrame(data[1:], columns=data[0])
  doacao_mes_atual = df.loc[df['NOME'] == 'DOAÇÕES', NOME_MES].values[0]
  df_doacoes = df[df['NOME'] == 'DOAÇÕES'][[NOME_MES]]
  doacao_mes_atual_str = f'DOAÇÕES {NOME_MES}: R$ {doacao_mes_atual}'
  print(doacao_mes_atual_str)

def get_trabalhos_mes():
  FILTRO= aux.proximo_sabado().strftime("/%m/")
  aux.montar_headers('| CALENDARIO |')
  df = pd.DataFrame(sh.worksheet("Calendário de Giras 2025").get('A:C'))
  df=df[df[0].str.contains(FILTRO)]
  for index, row in df.iterrows():
        if "Não haverá gira" in row[1]:
            output_string = f"{row[0]} - Não haverá gira"
        else:
            output_string = f"{row[0]} - {row[1]}"
        print(output_string)


def get_agenda_completa():
    hoje = datetime.now()
    mes_corrente = hoje.month
    ano_corrente = hoje.year
    aux.montar_headers('| PROXIMAS GIRAS E TRABALHOS |')
    df = pd.DataFrame(sh.worksheet("Calendário de Giras 2025").get('A:G'))
    df.columns = ['DATA', 'DESCRICAO', 'RESPONSAVEL','PORTEIRA','PREGIRA','APOIO','TAB. COROADOS']
    df['DATA'] = pd.to_datetime(df['DATA'], format="%d/%m/%Y", errors='coerce')
    # hoje = datetime.now().strftime("%d/%m/%Y")
    # df = df[df['DATA'] >= pd.to_datetime(hoje, format="%d/%m/%Y")]  #Retorna todos os trabalohs futuros
    df = df[
        (df['DATA'].dt.month == mes_corrente) &
        (df['DATA'].dt.year == ano_corrente) &
        (df['DATA'] > hoje)
    ]
    for index, row in df.iterrows():
        if "Não haverá gira" in row['DESCRICAO']:
            output_string = f"{row['DATA'].strftime('%d/%m/%Y')} - *Não haverá gira*"
        else:
                output_string = (
                f"{row['DATA'].strftime('%d/%m/%Y')} - {row['DESCRICAO']} "
            )
        if pd.notna(row['RESPONSAVEL']):
          output_string += f"Responsável: {row['RESPONSAVEL']}"

        if pd.notna(row['PREGIRA']):
          pregira_formatado = row['PREGIRA'].replace("; ", "\n")
          output_string += f"\nPré gira: {pregira_formatado}\n"

        if pd.notna(row['TAB. COROADOS']):
          output_string += f"Tab. Coroados: SIM\n"
          # output_string += f"Tab. Coroados: {row['TAB. COROADOS']}"
        print(output_string)

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



def para_filhos():
 mensagem_padrao()
 get_gira_semana()
 get_trabalhos_mes()
 get_cambones()
 get_tarefas()

def para_dirigentes():
 get_gira_semana()
 get_agenda_completa()
 get_cambones_dirigentes()
 get_tarefas()



# para_dirigentes()
# para_filhos()
get_aniversarios()