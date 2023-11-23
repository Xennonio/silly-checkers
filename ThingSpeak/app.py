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

# Import necessary libraries
from flask import Flask, render_template, request, redirect, session, jsonify

# Create a Flask web application
app = Flask(__name__, static_url_path='/static')

# Define a route for the root URL '/'
@app.route('/')
def index():
    return render_template('layout.html')

@app.route('/handle_click', methods=['POST'])
def handle_click():
    # Get the clicked cell information from the request
    data = request.get_json()
    clicked_row = data['firstClick']
    clicked_col = data['secondClick']

    coord1 = chr(clicked_row['col'] + 97) + str(clicked_row['row'])
    coord2 = chr(clicked_col['col'] + 97) + str(clicked_col['row'])
    coords = coord1 + ', ' + coord2
    print(coords)

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

    # You can also return a response to the frontend if needed
    response = {'status': 'success'}
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)