#importando as bibliotecas
import os.path
from functools import wraps
from flask import Flask, url_for, jsonify, redirect, request, current_app, send_from_directory

# Inicializa o webserver
app = Flask(__name__)

# Funcao utilizada para suportar o request de json para ler os dados
# Retirado de https://gist.github.com/farazdagi/1089923
def support_jsonp(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
                callback = request.args.get('callback', False)
                if callback:
                        content = str(callback) + '(' + str(f(*args,**kwargs).data) + ')'
                        return current_app.response_class(content,mimetype='application/javascript')
                else:
                        return f(*args, **kwargs)
        return decorated_function

# Leitura do arquivo de status
@app.route('/status')
@support_jsonp
def status():
        f = open('status.data', 'r') # Abre arquivo de dados com informacoes salvas pelo sistema
        status = f.readline()
        f.close()
        statusJson = {"status":status}
        resp = jsonify(statusJson)
        resp.status_code = 200
        return resp # Grava dados lidos em um json que e capturado pela interface web

# Leitura da posicao
@app.route('/position')
@support_jsonp
def position():
       f = open('position.data', 'r') # Abre arquivo de dados com informacoes salvas pelo sistema
       position = int(f.readline())
       f.close()
       positionJson = {"position":position}
       resp = jsonify(positionJson)
       resp.status_code = 200
       return resp # Grava dados lidos em um json que e capturado pela interface web

# Leitura do sensor de luz
@app.route('/light')
@support_jsonp
def light():
        f = open('light.data', 'r') # Abre arquivo de dados com informacoes salvas pelo sistema
        light = int(f.readline())
        f.close()
        lightJson = {"light":light}
        resp = jsonify(lightJson)
        resp.status_code = 200
        return resp # Grava dados lidos em um json que e capturado pela interface web

# Leitura do painel solar
@app.route('/panel')
@support_jsonp
def panel():
        f = open('panel.data', 'r') # Abre arquivo de dados com informacoes salvas pelo sistema
        panel = f.readline()
        f.close()
        panelJson = {"panel":panel}
        resp = jsonify(panelJson)
        resp.status_code = 200
        return resp # Grava dados lidos em um json que e capturado pela interface web

if __name__ == '__main__':
        app.run(debug=False, host="200.18.97.122", port=80) # Roda o webserver no ip indicado
