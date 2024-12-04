import sys
from montarDF import abrir_planilha,GETTarefas,GETAniversarios,GETCalendario,GETCambones,GETFaxina,GETmensalidades,GETContas
from auxiliares import  mensagem_padrao

def mensagensGrupo():
    sys.stdout = open('outputs\mensagensGrupo.txt', 'w', encoding='utf-8')
    mensagem_padrao()
    GETTarefas()
    GETFaxina()
    GETAniversarios()
    sys.stdout = sys.__stdout__

def mensagensDirigentes():
    sys.stdout = open('outputs\mensagensDirigentes.txt', 'w', encoding='utf-8')
    print("Status do Terreiro: Mensalidades,Contas e Agenda")
    GETmensalidades()
    GETContas()
    GETCalendario()
    sys.stdout = sys.__stdout__

#mensagensDirigentes()
GETmensalidades()