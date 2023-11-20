# -- Importação das bibliotecas necessárais --

import pyautogui
import pyperclip
import time
import DobotDllType as dType

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

# para sabermos as coordenadas de cada casa do tabuleiro precisamos do Dobot em mãos
Board = {
    1: (1, 2, 0),
    2: (3, 1, 5),
    3: (6, 3, 0),
    # 4: coord_4 = (x, y, z)
    # ...
}

history_transcription = '' # salvar o histórico de jogadas do jogo
turn = 0 # contador de turnos
ac_whites, ac_blacks = [], [] # localização atual das pedras

# setup do Dobot Magician
def Dobotsetup():
    api = dType.load() # Objeto que acessa as funções da API Dobot.

    # valores de exemplo
    portName = ""
    baudrate = 115200

    velocity = 100
    acceleration = 100

    xh = 250
    yh = 0
    zh = 50
    rh = 0

    dType.ConnectDobot(api, portName, baudrate)

    dType.SetQueuedCmdStartExec() # definir a utilização de comandos consecutivos no Queue

    dType.SetPTPCommonParams(api, velocity, acceleration, isQueued = 1) # ajustar velocidade e aceleração do braço

    dType.SetHomeParams(api, xh, yh, zh, rh, isQueued = 1) # Definição da posição inicial

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
    global ac_whites, ac_blacks
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

    # transformar em uma lista
    positionW, positionB = list(positionW.split(',')), list(positionB.split(','))

    ac_blacks = positionB
    ac_whites = positionW

# executar os movimentos do Dobot para a coordenada 1 e depois para a 2
def dobotmoves(coord1, coord2):
    dType.SetHomeCmd(api, homeCmd = 0, isQueued = 1) # volta para a posição home

    # ir até a 1ª coordenada (com preferência sem esbarrar nas pedras)
    dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode, coord1[0], coord1[1], zh, 0, isQueued = 1)
    dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode, coord1[0], coord1[1], coord1[2], 0, isQueued = 1)

    # utilizar o periférico da ventosa para prender a pedra
    dType.SetEndEffectorSuctionCup(api, enableControl = 1, suction = 1, isQueued = 1)

    # ir até a 2ª coordenada
    dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode, coord1[0], coord1[1], zh, 0, isQueued = 1)
    dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode, coord2[0], coord2[1], zh, 0, isQueued = 1)
    dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode, coord2[0], coord2[1], coord2[2], 0, isQueued = 1)

    # soltar a pedra
    dType.SetEndEffectorSuctionCup(api, enableControl = 1, suction = 0, isQueued = 1)

    dType.QueuedCmdStartExec()

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

# -- Setup inicial para o funcionamento do Dobot Magician (só um rascunho, visto que agora não temos acesso ao braço) --
Dobotsetup()

# -- Movimentação em função do GuiNN checkers --

# sensor captura a jogada do oponente e envia para o GuiNN checkers

# Abrir o GuiNN checkers
pyautogui.hotkey('alt', 'tab')
time.sleep(0.3)
pyautogui.moveTo(415, 601)

while True:
    # realiza um turno e salva a transcrição do jogo
    play()

    turn += 1
    # recebe as transcrições atuais (exemplo)
    input_transcription = transcription_text[41:]

    # recebe as posições atuais (exemplo)
    position = position_text

    # calcular a posição atual das pedras
    positionsplit(position)

    # salvar o movimento do robô e do jogador
    transcription = transcript(input_transcription)
    dobotmove = transcription
    coords = dobotmove.replace('x', '-')
    b1, b2 = map(int, coords.split('-'))

    # salvar coordenadas iniciais e finais da pedra
    coord1 = Board[b1]
    coord2 = Board[b2]

    # realizar os comandos no braço robótico
    dobotmove(coord1, coord2)