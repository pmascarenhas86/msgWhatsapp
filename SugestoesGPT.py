from tabulate import tabulate
from datetime import datetime
import calendar
import pandas as pd
import locale
from auxiliares import montar_headers, abrir_planilha, imprimir_lista_formatada, limitar_caracteres, imprimir_dados
import numpy as np

locale.setlocale(locale.LC_ALL, 'pt_BR.utf8')

def get_nome_mes_atual():
    return calendar.month_name[datetime.now().month].upper()

def abrir_e_obter_planilha(ano):
    return abrir_planilha().worksheet(str(ano))

def obter_df_de_planilha(worksheet, inicio, fim):
    data = worksheet.get(f'{inicio}:{fim}')
    df = pd.DataFrame(data[1:], columns=data[0])
    return df

def get_mensalidades(worksheet, nome_mes_atual):
    print(f'\nMês de referência: {nome_mes_atual.upper()}')
    total_arrecadado_cell = worksheet.find("Total Arrecadado")
    df = obter_df_de_planilha(worksheet, 'A2', f'Z{total_arrecadado_cell.row}')
    print(df)
    df = pd.concat([df['NOME'], df[nome_mes_atual.upper()]], ignore_index=True, axis=1, join="outer")
    df.columns = ['NOME', 'VALOR PAGO']

    montar_headers('| MENSALIDADES PAGAS |')
    adimplente = df.dropna()
    imprimir_dados('arquivo', adimplente)

    montar_headers('| MENSALIDADES EM ABERTO |')
    df_em_aberto = df[df['VALOR PAGO'].isna()]
    valores_coluna_0 = [linha[0] for linha in df_em_aberto.to_dict(index=False, orient='split')['data']]
    string_formatada = limitar_caracteres(str(valores_coluna_0)).replace("'", '').replace("[", '').replace("]", '')
    print(string_formatada)
    print(f'Valor em aberto: R$. {len(df_em_aberto) * 125}')

def get_doacoes(worksheet, nome_mes_atual):
    montar_headers('| DOAÇÕES DO MÊS |')

    total_arrecadado_cell = worksheet.find("Total Arrecadado")
    data = worksheet.get('A2:Z' + str(total_arrecadado_cell.row))
    df = pd.DataFrame(data[1:], columns=data[0])
    df = df.fillna(value='0,00')

    filtro_doacao = (df['NOME'] == 'DOAÇÕES') & (df[nome_mes_atual] != '') & (df[nome_mes_atual] != '0')
    doacao_mes_atual = df.loc[filtro_doacao, nome_mes_atual].values

    df_doacoes = df[df['NOME'] == 'DOAÇÕES'][[nome_mes_atual.upper()]]
    doacao_mes_atual_str = f'DOAÇÕES {nome_mes_atual}: {doacao_mes_atual}'
    print(doacao_mes_atual_str)

def get_contas(worksheet, nome_mes_atual):
    total_despesas_cell_inicio = worksheet.find("DESPESAS")
    total_despesas_cell_final = worksheet.find("Total Despesas")
    df = obter_df_de_planilha(worksheet, f'A{total_despesas_cell_inicio.row}', f'Z{total_despesas_cell_final.row}')
    df = pd.concat([df['DESPESAS'], df[nome_mes_atual.upper()]], ignore_index=True, axis=1, join="outer")
    df = df.replace(to_replace='None', value='NaN').dropna()
    df.columns = ['DESPESAS', 'VALOR PAGO']

    print(f'\nMês de referência: {nome_mes_atual.upper()}')
    montar_headers('| CONTAS PAGAS |')
    imprimir_dados('arquivo', df)

def get_tarefas(worksheet, nome_mes_atual):
    montar_headers('| ATIVIDADES DO MÊS |')
    df = obter_df_de_planilha(worksheet, 'A2','G10')
    print(df)
    df_tarefas = df[['ATIVIDADE']]
    df_mes_atual = df[['ATIVIDADE', nome_mes_atual]]
    print(df_mes_atual)
    atividades_mes_atual = []
    for index, row in df.iterrows():
        if row['ATIVIDADE'] != '':
            atividade = row['ATIVIDADE'].split('\n', 1)[0] if ':' in row['ATIVIDADE'] else row['ATIVIDADE']
            atividades_mes_atual.append([atividade.strip(), row[nome_mes_atual]])

    df = pd.DataFrame(atividades_mes_atual, columns=['ATIVIDADE', nome_mes_atual])
    print('')
    imprimir_dados('arquivo', df)
    print('Para maiores detalhes: https://t.ly/WtoHr')


def main():
    nome_mes_atual = get_nome_mes_atual()
    worksheet = abrir_e_obter_planilha(2024)
    #get_mensalidades(worksheet, nome_mes_atual)
    #get_doacoes(worksheet, nome_mes_atual)
    #get_contas(worksheet, nome_mes_atual)
    get_tarefas(worksheet, nome_mes_atual)

if __name__ == "__main__":
    main()
