# -- Importação das bibliotecas necessárais --

import pyautogui
import pyperclip
import time
import urllib3

# tabuleiro com uma coordenada em cada entrada (é necessário pegar os valores com o braço):
#   32  31  30  29
# 28  27  26  25
#   24  23  22  21
# 20  19  18  17
#   16  15  14  13
# 12  11  10  09
#   08  07  06  05
# 04  03  02  01

# -- Variáveis utilizadas na I.A. e o no braço --
history_transcription = '' # salvar o histórico de jogadas do jogo
turn = 0 # contador de turnos
ac_whites, ac_blacks, tmp_whites = [], [], [] # localização atual das pedras

# -- Variáveis utilizadas no sensor --
TSdata = 0 # quantidade de dados no ThingSpeak
http = urllib3.PoolManager() # criar uma instância para receber e enviar valores para o ThingSpeak
# Urls necessários para receber / enviar valores
ReadUrl = 'https://api.thingspeak.com/channels/2351586/feeds.json?results='
UpdateUrl = 'https://api.thingspeak.com/channels/2351586/status.json'
# coordenadas das casas do tabuleiro para o mouse
Mouse_Coordinates = {
    1 : (460, 538),
    2 : (332, 538),
    3 : (203, 538),
    4 : (75, 538),
    5 : (524, 474),
    6 : (396, 474),
    7 : (267, 474),
    8 : (139, 474),
    9 : (460, 410),
    10 : (332, 410),
    11 : (203, 410),
    12 : (75, 410),
    13 : (524, 346),
    14 : (396, 346),
    15 : (267, 346),
    16 : (139, 346),
    17 : (460, 281),
    18 : (332, 281),
    19 : (203, 281),
    20 : (75, 281),
    21 : (524, 217),
    22 : (396, 217),
    23 : (267, 217),
    24 : (139, 217),
    25 : (460, 153),
    26 : (332, 153),
    27 : (203, 153),
    28 : (75, 153),
    29 : (524, 89),
    30 : (396, 89),
    31 : (267, 89),
    32 : (139, 89)
}

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

# função para realizar o turno do robô e copiar as transcrições e posições atuais
def play_turn():
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
    else:
        # salvar as posições e a transcrição atual do jogo
        position_text = pyperclip.paste()
        pyautogui.hotkey('ctrl', 'c')
        transcription_text = pyperclip.paste()

# função para realizar o turno do jogador
def sensor_move():
    global TSdata, ac_blacks, ac_whites, position_text

    # copia as posições atuais do jogo
    pyautogui.hotkey('c')
    position_text = pyperclip.paste()

    response = http.request('GET', UpdateUrl)
    # determinar a quantidade de dados atuais
    points = splitdata(response).count('{')
    TSdata = points
    # enquanto não forem recebidos 2 coordenadas continuar atualizando
    while points != TSdata + 2:
        response = http.request('GET', UpdateUrl)
        points = splitdata(response).count('{')
    # caso contrário, salvar as coordenadas (data1, data2)
    else:
        # ler todos os valores recebidos
        response = http.request('GET', ReadUrl + str(points))
        # pegar o feed de valores
        coordinates = splitdata(response)
        # colocá-los em lista
        coordinates = coordinates[2:len(coordinates) - 1].split('},{')
        # pegar os últimos 2 dadps da tabela
        data1, data2 = coordinates[len(coordinates) - 2], coordinates[len(coordinates) - 1]
        # encontrar os últimos valores de "field1":"value" e salvá-los em data1 e data2
        valueindex1, valueindex2 = data1.find('"field1":"') + len('"field1":"'), data2.find('"field1":"') + len('"field1":"')
        data1, data2 = data1[valueindex1:len(data1) - 1], data2[valueindex2:len(data2) - 1]
    play_mouse((int(data1), int(data2)))
    # atualizar a quantidade de dados no ThingSpeak
    TSdata = points
    # copiar posição atual após a jogada
    pyautogui.hotkey('c')
    # determinar se a jogada é inválida e jogar novamente se for
    if pyperclip.paste() == position_text:
        sensor_move()
    # determinar se houve um vencedor após a jogada
    positionsplit(position_text)
    winner(ac_blacks, ac_whites)
    # retornar para as coordenadas do botão
    pyautogui.moveTo(415, 601)

# função para arrumar os dados
def splitdata(response):
	data = str(response.data)
	# devolver apenas o feed de dados
	feedstart = data.find('[')
	feedend = data.find(']')
	feeds = data[feedstart:feedend]
	return feeds

# função para determinar se há um ganhador
def winner(blacklist, whitelist):
    if blacklist == ['']:
        print('as brancas ganharam')
        exit()
    if whitelist == ['']:
        print('as pretas ganharam')
        exit()

# função para realizar a jogada real no GuiNN
def play_mouse(coord):
    # realizar jogada no programa
    for i in coord:
        pyautogui.moveTo(Mouse_Coordinates[i][0], Mouse_Coordinates[i][1])
        pyautogui.click()

# -- Movimentação em função do GuiNN checkers --

# abrir o GuiNN checkers
pyautogui.hotkey('alt', 'tab')
time.sleep(0.3)
pyautogui.moveTo(415, 601)

while True:
    # realizar a jogada da pessoa
    sensor_move()

    # realizar a jogada do GuiNN Checkers
    play_turn()

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