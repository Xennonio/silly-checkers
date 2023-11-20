import urllib3

# criar uma instância para receber e enviar valores para o ThingSpeak
http = urllib3.PoolManager()

# Urls necessários para receber / enviar valores
WriteUrl = 'https://api.thingspeak.com/update?api_key=78OAWCS0GMLGR1C8&field1='
ReadUrl = 'https://api.thingspeak.com/channels/2351586/feeds.json?results='
UpdateUrl = 'https://api.thingspeak.com/channels/2351586/status.json'

# função para arrumar os dados
def splitdata(response):
	data = str(response.data)
	# devolver apenas o feed de dados
	feedstart = data.find('[')
	feedend = data.find(']')
	feeds = data[feedstart:feedend]
	return feeds

while True:
	# valores das coordenadas segundo o BitBoard
	coord1 = input('Posição Inicial: ')
	coord2 = input('Posição Final: ')
	# atualizar o status
	response = http.request('GET', UpdateUrl)
	# determinar a quantidade de dados atuais
	points = splitdata(response).count('{')
	newpoints = points
	# enviar o primeiro valor para o ThingSpeak
	while newpoints == points:
		response = http.request('GET', WriteUrl + coord1)
		response = http.request('GET', UpdateUrl)
		newpoints = splitdata(response).count('{')
	# esperar atualizar a quantidade de dados
	while points == newpoints:
		response = http.request('GET', UpdateUrl)
		newpoints = splitdata(response).count('{')
	else:
		# igualar a quantidade de dados antiga e nova
		points = newpoints
		# enviar o novo valor até o ThingSpeak receber
		while newpoints == points:
			response = http.request('GET', WriteUrl + coord2)
			response = http.request('GET', UpdateUrl)
			newpoints = splitdata(response).count('{')

'''
# ler todos os valores recebidos
response = http.request('GET', ReadUrl + str(newpoints))
# pegar o feed de valores
coordinates = splitdata(response)
# colocá-los em lista
coordinates = coordinates[2:len(coordinates) - 1].split('},{')
# pegar os últimos 2 dadps da tabela
data1, data2 = coordinates[len(coordinates) - 2], coordinates[len(coordinates) - 1]
# encontrar os últimos valores de "field1":"value" e salvá-los em data1 e data2
valueindex1, valueindex2 = data1.find('"field1":"') + len('"field1":"'), data2.find('"field1":"') + len('"field1":"')
data1, data2 = data1[valueindex1:len(data1) - 1], data2[valueindex2:len(data2) - 1]
'''