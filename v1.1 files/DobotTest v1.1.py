# -- Importação das bibliotecas necessárais --

import pyautogui
import pyperclip
import time

# -- Definições de variáveis e constantes usadas --

# tabuleiro com uma coordenada em cada entrada (é necessário pegar os valores com o braço):
#   32  31  30  29
# 28  27  26  25
#   24  23  22  21
# 20  19  18  17
#   16  15  14  13
# 12  11  10  09
#   08  07  06  05
# 04  03  02  01

history_transcription = '' # salvar o histórico de jogadas do jogo
turn = 0 # contador de turnos
ac_whites, ac_blacks, tmp_whites = [], [], [] # localização atual das pedras

# função para retornar as jogadas do jogador e da IA
def transcript(txt):
    # remover o cabeçário e elementos inúteis
    global history_transcription
    global turn

    # salvar o histórico de jogadas anteriores
    turnindex = txt.find(str(turn) + '.')
    history_transcription = txt[:turnindex]

    txt = txt[len(history_transcription):len(txt) - 2]

    # retornar a jogada do GuiNN checkers
    return txt.split(' ')[2]
    
# separar as posições das pedras brancas e pretas
def positionsplit(txt):
    global ac_whites, ac_blacks, tmp_whites
    # remover o cabeçário e elementos inúteis
    txt = txt[2:len(txt) - 1]

    # dividir position em posição de brancas e pretas
    positionW = ''
    for l in txt[1:]:
        if l == ':':
            break
        else:
            positionW += l
    positionB = txt[len(positionW) + 3:]

    # salvar as posições da partida anterior
    if turn > 2:
        tmp_whites = ac_whites

    # transformar em uma lista
    positionW, positionB = list(positionW.split(',')), list(positionB.split(','))

    ac_blacks = positionB
    ac_whites = positionW

# função para realizar um turno e copiar as transcrições e posições atuais
def play():
    global transcription_text, position_text, ac_blacks, ac_whites

    # copia as posições atuais do jogo
    pyautogui.hotkey('c')
    position_text = pyperclip.paste()

    # realizar uma partida com o robô (exemplo de teste)
    pyautogui.click()

    # enquanto uma jogada ainda não foi feita, continuar esperando, a não ser que haja um vencedor
    while pyperclip.paste() == position_text:
        pyautogui.hotkey('c')
        positionsplit(position_text)
        winner(ac_blacks, ac_whites)
    # caso contrário faça a jogada seguinte
    else:
        position_text = pyperclip.paste()
        pyautogui.click()
    
    # repetir o mesmo processo anterior para que ambos os jogadores façam uma jogada, contando como uma rodada inteira
    while pyperclip.paste() == position_text:
        pyautogui.hotkey('c')
        positionsplit(position_text)
        winner(ac_blacks, ac_whites)
    else:
        # salvar as posições e a transcrição atual do jogo
        position_text = pyperclip.paste()
        pyautogui.hotkey('ctrl', 'c')
        transcription_text = pyperclip.paste()

# função para determinar se há um ganhador
def winner(blacklist, whitelist):
    if blacklist == ['']:
        print('as brancas ganharam')
        exit()
    if whitelist == ['']:
        print('as pretas ganharam')
        exit()

# -- Movimentação em função do GuiNN checkers --

# sensor captura a jogada do oponente e envia para o GuiNN checkers

# abrir o GuiNN checkers
pyautogui.hotkey('alt', 'tab')
time.sleep(0.3)
pyautogui.moveTo(415, 601)

while True:
    play()

    turn += 1
    # recebe as transcrições atuais (exemplo)
    input_transcription = transcription_text[41:]

    # recebe as posições atuais (exemplo)
    position = position_text

    # salvar a posição atual das pedras
    positionsplit(position)

    # salvar o movimento do robô e do jogador
    transcription = transcript(input_transcription)
    dobotmove = transcription
    coords = dobotmove.replace('x', '-')
    b1, b2 = map(int, coords.split('-'))

    # se a pedra movida acabou de virar uma rainha:
    if 'K' + str(b2) in ac_whites and 'K' + str(b1) not in tmp_whites:
        print('robô move a pedra em', b1, 'até', b2, 'e adiciona outra pedra em cima')
    # se a pedra já era uma rainha
    if 'K' + str(b2) in ac_whites and 'K' + str(b1) in tmp_whites:
        print('robô move a pedra em', b1, 'até', b2, 'duas vezes')
    # se a pedra não é uma rainha
    if 'K' + str(b2) not in ac_whites:
        print('robô move a pedra em', b1, 'até', b2)