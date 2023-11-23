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
	coords = input('Coordenadas (x, y): ')
	# atualizar o status
	response = http.request('GET', UpdateUrl)
	# determinar a quantidade de dados atuais
	points = splitdata(response).count('{')
	newpoints = points
	# enviar o valor para o ThingSpeak
	while newpoints == points:
		response = http.request('GET', WriteUrl + coords)
		response = http.request('GET', UpdateUrl)
		newpoints = splitdata(response).count('{')
	# esperar atualizar a quantidade de dados
	while points == newpoints:
		response = http.request('GET', UpdateUrl)
		newpoints = splitdata(response).count('{')
	else:
		# igualar a quantidade de dados antiga e nova
		points = newpoints