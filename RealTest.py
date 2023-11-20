# -- https://github.com/SERLatBTH/StarterGuide-Dobot-Magician-with-Python --
import DobotDllType as dType

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

dobotmoves((123, 123, 123), (12, 12, 12))