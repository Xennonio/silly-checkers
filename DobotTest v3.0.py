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
ac_whites, ac_blacks, tmp_whites, tmp_blacks = [], [], [], [] # localização atual e temporária das pedras
cap_b, cap_w = [], [] # lista de pedras capturadas
out_board = (1, 2, 3) # coordenada fora do tabuleiro

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
    global history_transcription, turn

    # salvar o histórico de jogadas anteriores
    turnindex = txt.find(str(turn) + '.') # 1. turno1, 2. turno2, ...
    history_transcription = txt[:turnindex]

    # remover partes inúteis
    txt = txt[len(history_transcription):len(txt) - 2]

    # retornar a jogada do GuiNN checkers e do jogador
    robot_move = txt.split(' ')[2]
    people_move = txt.split(' ')[1]

    return people_move, robot_move

# separar as posições das pedras brancas e pretas
def positionsplit(txt):
    global ac_whites, ac_blacks, tmp_whites, tmp_blacks
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
    if turn > 0:
        tmp_whites = ac_whites
        tmp_blacks = ac_blacks

    # transformar em uma lista
    positionW, positionB = list(positionW.split(',')), list(positionB.split(','))

    ac_blacks = positionB
    ac_whites = positionW

# função para realizar o turno do robô e copiar as transcrições e posições atuais
def play_turn():
    global transcription_text, position_text, ac_blacks, ac_whites
    # enquanto uma jogada ainda não foi feita, continuar esperando, a não ser que haja um vencedor
    while pyperclip.paste() == position_text:
        pyautogui.hotkey('c')
        positionsplit(pyperclip.paste())
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
    positionsplit(position_text)
    response = http.request('GET', UpdateUrl)
    # determinar a quantidade de dados atuais
    points = splitdata(response).count('{')
    TSdata = points
    # enquanto não for recebido 1 coordenada continuar atualizando
    while points != TSdata + 1:
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
        # pegar o último dado da tabela
        data1 = coordinates[len(coordinates) - 1]
        # encontrar o último valor de "field1":"value" e salvá-lo em data1
        valueindex1 = data1.find('"field1":"') + len('"field1":"')
        data1 = data1[valueindex1:len(data1) - 1]
    # realizar a jogada
    play_mouse(data1)
    # copiar posição atual após a jogada
    pyautogui.hotkey('c')
    # atualizar a quantidade de dados no ThingSpeak
    TSdata = points
    # determinar se a jogada é inválida e jogar novamente se for
    if pyperclip.paste() == position_text:
        sensor_move()
    # salvar posição atual
    position_text = pyperclip.paste()
    # determinar se houve um vencedor após a jogada
    positionsplit(position_text)
    winner(ac_blacks, ac_whites)

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
    # -- Notação padrão --
    #   b8  d8  f8  h8
    # a7  c7  e7  g7
    #   b6  d6  f6  h6
    # a5  c5  e5  g5
    #   b4  d4  f4  h4
    # a3  c3  e3  g3
    #   b2  d2  f2  h2
    # a1  c1  e1  g1

    # dividir a coordenada de notação padrão (start, end) em letra e número
    start, end = (coord.replace(' ', '')).split(',')
    sc1, sc2 = start[0], start[1] # (a3, end) -> (sc1, sc2) = (a, 3)
    ec1, ec2 = end[0], end[1] # (start, b5) -> (ec1, ec2) = (b, 5)
    coord1, coord2 = bitconv(sc1, int(sc2)), bitconv(ec1, int(ec2)) # converter para bitboard
    # realizar jogada no programa
    for i in (coord1, coord2):
        pyautogui.moveTo(Mouse_Coordinates[i][0], Mouse_Coordinates[i][1])
        pyautogui.click()

# conversor de notação convencional para bitboard
def bitconv(S, n):
    conv = {'a' : 4, 'b' : 8, 'c' : 3, 'd' : 7, 'e' : 2, 'f' : 6, 'g' : 1, 'h' : 5}
    if S in ['b', 'd', 'f', 'h']:
        coord = 8 * (n/2 - 1) + conv[S]
    else:
        coord = 8 * ((n + 1)/2 - 1) + conv[S]
    return coord

# executar os movimentos do Dobot para a coordenada 1 e depois para a 2
def execute(x, y, ac_piece, tmp):
    # se a pedra movida acabou de virar uma rainha:
    if 'K' + y in ac_piece and 'K' + x not in tmp:
        print('robô move a pedra em', x, 'até', y, 'e adiciona outra pedra em cima')
    # se a pedra já era uma rainha
    if 'K' + y in ac_piece and 'K' + x in tmp:
        print('robô move a pedra em', x, 'até', y, 'duas vezes')
    # se a pedra não é uma rainha
    if 'K' + y not in ac_piece:
        print('robô move a pedra em', x, 'até', y)

# remover pedras capturadas do tabuleiro
def dobotremove(x):
    print('robô remove a pedra', x, 'do tabuleiro')
    # out_board coordinate

# -- Movimentação em função do GuiNN checkers --

# abrir o GuiNN checkers
pyautogui.hotkey('alt', 'tab')
time.sleep(0.3)

while True:
    # realizar a jogada da pessoa
    sensor_move()

    # se uma pedra branca tiver sido capturada após a jogada das pretas
    if len(ac_whites) != len(tmp_whites):
        cap_w = [i for i in tmp_whites if i not in ac_whites] # pedras brancas capturadas
    else:
        cap_w = []

    # realizar a jogada do GuiNN Checkers
    play_turn()

    # se uma pedra preta tiver sido capturada após a jogada das brancas
    if len(ac_blacks) != len(tmp_blacks):
        cap_b = [i for i in tmp_blacks if i not in ac_blacks] # pedras pretas capturadas
    else:
        cap_b = []

    turn += 1
    # recebe as transcrições atuais (exemplo)
    input_transcription = transcription_text[41:]

    # salvar o movimento do robô e do jogador
    people_transcription, robot_transcription = transcript(input_transcription)
    peoplemove = people_transcription
    dobotmove = robot_transcription
    coords1 = peoplemove.replace('x', '-')
    coords2 = dobotmove.replace('x', '-')
    x1, y1 = coords1.split('-')
    x2, y2 = coords2.split('-')

    # -- Executá-los --
    execute(x1, y1, ac_blacks, tmp_blacks) # movimento das pretas

    # retirar pedras capturadas para fora do tabuleiro
    for i in cap_w:
        dobotremove(i)

    execute(x2, y2, ac_whites, tmp_whites) # movimento das brancas

    # retirar pedras capturadas para fora do tabuleiro
    for i in cap_b:
        dobotremove(i)

    print(cap_w, cap_b)