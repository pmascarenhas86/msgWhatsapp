import calendar
import pandas as pd
import warnings
import random
import locale
import numpy as np
from datetime import datetime
from tabulate import tabulate
from auxiliares import  montar_headers,abrir_planilha, imprimir_lista_formatada,limitar_caracteres,imprimir_dados


locale.setlocale(locale.LC_ALL, 'pt_BR.utf8')
warnings.simplefilter(action='ignore', category=FutureWarning)
month = datetime.now().month
year = datetime.now().year
NOME_MES = calendar.month_name[month].capitalize()
sh=abrir_planilha()
locale.setlocale(locale.LC_ALL, 'pt_BR.utf8')
warnings.simplefilter(action='ignore', category=FutureWarning)
sh=abrir_planilha()
# df = pd.DataFrame(sh.worksheet("Cambones").get('A1:Z'))
worksheet = sh.worksheet("Cambones")
lista_a = [
    'Elanisia', 'Kathya', 'Leticia', 'Luana', 'Paolla', 'Paulo',
    'Soraia', 'Thais', 'Walker', 'FICHAS', 'COPA', 'APOIO GERAL'
]
lista_b = [
    'Gustavo', 'Roseli', 'Emilly', 'Roseli', 'Marcia', 'Karine',
    'Maria Eduarda', 'Maria Eduarda', 'Etienne', 'Ricardo',
    'Bianca','Caroliny','Paulo V','Tatiane','Milena'
]

random.shuffle(lista_b)
data = {'MEDIUNS': lista_a}
df = pd.DataFrame(data)

meses = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho','Julho','Agosto','Setembro','Outubro','Novembro','Dezembro']
for mes in meses:
    nomes_mes = []
    ultimo_nome = None
    for _ in range(len(lista_a)):
        nome_selecionado = random.choice([nome for nome in lista_b if nome != ultimo_nome])
        nomes_mes.append(nome_selecionado)
        ultimo_nome = nome_selecionado
    df[mes] = nomes_mes

# table = tabulate(df, headers='keys', tablefmt='grid')
table = tabulate(df, headers='keys', tablefmt='fancy_grid')
print(f'\n',table)
# Enviar a tabela para a planilha
#worksheet.update('A20', 'MEDIUM DE CONSULTA')
# worksheet.update('B20:G20', [meses])
# worksheet.update('A21', [lista_a])
# worksheet.update('B21:G33', df.values.tolist())
