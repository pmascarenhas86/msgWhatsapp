from tabulate import tabulate
import calendar
import pandas as pd
import warnings
import locale
import numpy as np
from auxiliares import  *
from datetime import datetime, timedelta
locale.setlocale(locale.LC_ALL, 'pt_BR.utf8')
warnings.simplefilter(action='ignore', category=FutureWarning)



#Definindo Variaveis
sh=abrir_planilha()
NOME_MES = calendar.month_name[datetime.now().month].capitalize()

def GETmensalidades():
  sh=abrir_planilha_dirigentes()
  print(f'\nMês de referência: ', NOME_MES.upper())
  total_arrecadado_cell = sh.worksheet("2024").find("Total Arrecadado")
  df = pd.DataFrame(sh.worksheet("2024").get('A2:Z' + str(total_arrecadado_cell.row)))
  new_header = df.iloc[0]
  df = df[1:]
  df.columns = new_header
  df = pd.concat([df['NOME'], df[NOME_MES.upper()]], ignore_index=True, axis=1, join="outer")
  df.columns = ['NOME', 'VALOR PAGO']
  df = df[df['NOME'] != 'DOAÇÕES']
  montar_headers(f'| MENSALIDADES PAGAS |')
  adimplente = df.dropna()
  imprimir_dados('arquivo', adimplente)
  montar_headers('| MENSALIDADES EM ABERTO |')
  df=df[df['VALOR PAGO'].isna()]
  dict=df.to_dict(index=False,orient='split')
  valores_coluna_0 = [linha[0] for linha in dict['data']]
  string_formatada =  limitar_caracteres(str(valores_coluna_0)).replace("'",'').replace("[",'').replace("]",'')
  print(string_formatada)
  print('Valor em aberto: R$.',len(df)*125)


def GETDoacoes():
  sh=abrir_planilha_dirigentes()
  total_arrecadado_cell = sh.worksheet("2024").find("Total Arrecadado")
  data = sh.worksheet("2024").get('A2:Z' + str(total_arrecadado_cell.row))
  df = pd.DataFrame(data[1:], columns=data[0])
  df= df.fillna(value='0,00')
  NOME_MES = datetime.now().strftime('%B').upper()  # Obtém o nome do mês atual em maiúsculas
  filtro_doacao = (df['NOME'] == 'DOAÇÕES') & (df[NOME_MES] != '') & (df[NOME_MES] != '0')
  doacao_mes_atual = df.loc[filtro_doacao, NOME_MES].values
  df_doacoes = df[df['NOME'] == 'DOAÇÕES'][[NOME_MES.upper()]]
  doacao_mes_atual_str = f'DOAÇÕES {NOME_MES}: {doacao_mes_atual}'
  montar_headers('| DOAÇÕES |')

  print(doacao_mes_atual_str)


def GETContas():
  sh=abrir_planilha_dirigentes()
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
  print(f'\nMês de referência: ', NOME_MES.upper())
  montar_headers('| CONTAS PAGAS |')
  imprimir_dados('arquivo', df)

def GETTarefas():
  montar_headers(f'| ATIVIDADES DO MÊS |')
  data = sh.worksheet("Rodizio de Tarefas").get('A3:AA100')
  df = pd.DataFrame(data[1:], columns=data[0])
  df_tarefas = df[['ATIVIDADE']]
  df_mes_atual = df[['ATIVIDADE', NOME_MES.upper()]]
  atividades_mes_atual = []
  for index, row in df.iterrows():
      if row['ATIVIDADE'] != '':
          atividade = row['ATIVIDADE'].split('\n', 1)[0]
          atividades_mes_atual.append([atividade.strip(), row[NOME_MES.upper()]])
  df = pd.DataFrame(atividades_mes_atual, columns=['ATIVIDADE', NOME_MES.upper()])
  imprimir_dados('arquivo', df)
  print('Para maiores detalhes: https://t.ly/WtoHr')

def GETFaxina():
    FILTRO_FAXINA = datetime.now().strftime('/%m/%Y')
    montar_headers('| FAXINA |')
    df = pd.DataFrame(sh.worksheet("Rodízio de Faxina").get('E:H'))
    df.columns = ['DATA', 'NOME_MES', 'TIPO', 'DataPgto']
    df = df[df['DATA'].str.contains(FILTRO_FAXINA)]
    df = df.sort_values(by='DATA', ascending=True, na_position='first')
    df['DataPgto'] = 'Data limite para pagamento: ' + df['DataPgto']
    df['mensagem'] = df['DATA'] + ' - ' + df['NOME_MES'] + ' ' + df['TIPO'] + ' - ' + df['DataPgto']
    mensagem_faxina()
    print()
    print("\n".join(df['mensagem']))
    mensagem_pos_faxina()


def GETAniversarios():
  sh=abrir_planilha_dirigentes()
  NOME_MES = calendar.month_name[datetime.now().month].capitalize()
  #  https://docs.google.com/spreadsheets/d/19T-4rB4sB5LSZsFZzrdiMIR0OAO5xLC5epabzU_b4qA/edit?resourcekey=&gid=1193522622#gid=1193522622
  FILTRO_ANIVERSARIO= datetime.now().strftime('/%m')
  montar_headers('| ANIVERSARIANTES |')
  df_plan_dadosMediuns = pd.DataFrame(sh.worksheet("Respostas ao formulário 1").get_all_records())
  df=pd.concat([df_plan_dadosMediuns['Data de Nascimento:'].apply(str).str[:5],df_plan_dadosMediuns['Nome:']],axis=1,join="outer",ignore_index=True)
  # df = df[df['Nome'] != 'DOAÇÕES']
  df=df[df[0].str.contains(FILTRO_ANIVERSARIO)]
  df.columns=['DATA','ANIVERSARIANTE']
  df=df.sort_values(by='DATA', ascending=True, na_position='first')
  imprimir_dados('arquivo', df)

def GETCambones():
    df = pd.DataFrame(sh.worksheet("Cambones").get('A1:Z'))
    new_header = df.iloc[0]
    df = df[1:]
    df.columns = new_header.str.upper()
    df = pd.concat([df['MEDIUM DE CONSULTA'], df[NOME_MES.upper()]], ignore_index=True, axis=1, join="outer")
    df.columns = ['MEDIUM DE CONSULTA', 'CAMBONE']
    montar_headers('| CAMBONES |')
    df = df.dropna()
    imprimir_dados('arquivo', df)

def getCamboneDirigentes():
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
    montar_headers('| CAMBONES |')
    imprimir_dados('arquivo', df)





def GETGiraSemana():
  FILTRO= proximo_sabado().strftime("%d/%m")
  montar_headers('| GIRA ATUAL |')
  df = pd.DataFrame(sh.worksheet("Calendário de Giras").get('A:H'))
  df=df[df[0].str.contains(FILTRO)]
  df.columns=['DATA','LINHA','RESPONSAVEL','PORTEIRAS','PRE_GIRA','APOIO','TRABALHO_FECHADO','FAXINA']
  if df['LINHA'].iloc[0]=='Não haverá Gira':
     output_string = f"Neste sábado: {df['DATA'].iloc[0]}\n" \
     f"ATENÇÃO: {df['LINHA'].iloc[0]}\n" \

  else:
      output_string = f"Neste sábado: {df['DATA'].iloc[0]}\n" \
      f"Linha de trabalho: {df['LINHA'].iloc[0]}\n" \
      f"Responsável(is): {df['RESPONSAVEL'].iloc[0]}\n" \
      # f"Porteiras: {df['PORTEIRAS'].iloc[0]}\n" \
      f"Atividade pre-gira: {df['PRE_GIRA'].iloc[0]}\n" \
      # f"Mediuns de apoio: {df['APOIO'].iloc[0]}\n" \
      # f"Trabalho com coroados: {df['TRABALHO_FECHADO'].iloc[0]}\n" \
      f"Grupo de Faxina: {df['FAXINA'].iloc[0]}\n"
  print(output_string)
  # imprimir_dados('tela', df)

def GETValores():
  sh=abrir_planilha_dirigentes()
  Doacoes = sh.worksheet("2024").find("DOAÇÕES")
  data = sh.worksheet("2024").get_all_values()
  df = pd.DataFrame(data[1:], columns=data[0])
  doacao_mes_atual = df.loc[df['NOME'] == 'DOAÇÕES', NOME_MES].values[0]
  df_doacoes = df[df['NOME'] == 'DOAÇÕES'][[NOME_MES]]
  doacao_mes_atual_str = f'DOAÇÕES {NOME_MES}: R$ {doacao_mes_atual}'
  print(doacao_mes_atual_str)

def GETTrabalhosMes():
  FILTRO= proximo_sabado().strftime("/%m/")
  montar_headers('| CALENDARIO |')
  df = pd.DataFrame(sh.worksheet("Calendário de Giras").get('A:C'))
  df=df[df[0].str.contains(FILTRO)]
  for index, row in df.iterrows():
        if "Não haverá gira" in row[1]:
            output_string = f"{row[0]} - Não haverá gira"
        else:
            output_string = f"{row[0]} - {row[1]}"
        print(output_string)

from datetime import datetime
import pandas as pd

def getTrabalhosFuturos():
    hoje = datetime.now()
    mes_corrente = hoje.month
    ano_corrente = hoje.year
    montar_headers('| PROXIMAS GIRAS E TRABALHOS |')
    df = pd.DataFrame(sh.worksheet("Calendário de Giras").get('A:G'))
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


def MensagemDoMesFilhos():
 mensagem_padrao()
 GETGiraSemana()
 GETTrabalhosMes()
 GETCambones()
 GETFaxina()
 GETTarefas()

def MensagemDoMesDirigentes():
#  mensagem_padrao()
 GETGiraSemana()
 getTrabalhosFuturos()
 getCamboneDirigentes()
 GETFaxina()
 GETTarefas()


MensagemDoMesFilhos()
# MensagemDoMesDirigentes()
# mensagem_padrao()
# mensagem_faxina()
# GETGiraSemana()
# GETmensalidades()
# GETAniversarios()
# GETCambones()
# GETFaxina()
# GETTrabalhosMes()
# GETTarefas()
# GETDoacoes()
# GETContas()
# getTrabalhosFuturos()
