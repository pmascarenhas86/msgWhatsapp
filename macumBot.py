import datetime
import time
import pyperclip
import webbrowser
import pyautogui
import sys
import pyautogui
import time
import pygetwindow as gw
import ObterMensagensViaGS

def enviar_mensagens_via_whatsapp(contato):
    hora_atual = datetime.datetime.now().hour
    # Cria uma mensagem com base na hora
    if 5 <= hora_atual < 12:
        mensagem = "Bom dia!"
    elif 12 <= hora_atual < 18:
        mensagem = "Boa tarde!"
    else:
        mensagem = "Boa noite!"

    mensageiro   ='https://web.whatsapp.com/'
    webbrowser.open_new(mensageiro)
    time.sleep(10)
    pyautogui.press('tab',presses=5)
    time.sleep(2)
    pyautogui.press('enter')
    time.sleep(1)
    pyautogui.typewrite(contato, interval=0.1)  # useful for entering text, newline is Enter
    pyautogui.press('enter')
    pyautogui.keyDown('ctrl')
    pyautogui.press('v')
    pyautogui.keyUp('ctrl')
    time.sleep(2)
    pyautogui.typewrite(mensagem+ ' Trago as informacoes do mes', interval=0.1)
    fo = open('output.txt', 'r', encoding='utf-8').read()
    pyperclip.copy(fo)
    pyautogui.keyDown('ctrl')
    pyautogui.press('enter')
    pyautogui.press('V')
    pyautogui.keyUp('ctrl')
    pyautogui.press('enter')
    pyautogui.keyDown('ctrl')
    pyautogui.press('F4')


def personagem(tipoMensagem):
    if tipoMensagem == 'Dirigentes':
     personagem='ze2.jpeg'
     ObterMensagensViaGS.mensagensDirigentes('arquivo')
    elif tipoMensagem == "Inicio Mes":
     ObterMensagensViaGS.mensagensGrupo('arquivo')
     personagem='ze1.jpeg'
    else:
     personagem='Maria.jpeg'

    pyautogui.hotkey('win', 'r')
    pyautogui.typewrite('d:\\automacao_whatsapp\\img\\'+personagem)
    pyautogui.press('enter')
    time.sleep(3)
    imgWindow=gw.getWindowsWithTitle(personagem)[0]
    imgWindow.activate()
    pyautogui.hotkey('ctrl', 'c')
    time.sleep(1)
    imgWindow.close()


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("INFORME OS VALORES")

    else:
        personagem(sys.argv[1])
        enviar_mensagens_via_whatsapp(sys.argv[2])
