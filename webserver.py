import os.path
from functools import wraps
from flask import Flask, url_for, jsonify, redirect, request, current_app, send_from_directory

app = Flask(__name__)

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

@app.route('/status')
@support_jsonp
def status():
        f = open('status.data', 'r')
        status = f.readline()
        f.close()
        statusJson = {"status":status}
        resp = jsonify(statusJson)
        resp.status_code = 200
        return resp


@app.route('/position')
@support_jsonp
def position():
       f = open('position.data', 'r')
       position = int(f.readline())
       f.close()
       positionJson = {"position":position}
       resp = jsonify(positionJson)
       resp.status_code = 200
       return resp

@app.route('/light')
@support_jsonp
def light():
        f = open('light.data', 'r')
        light = int(f.readline())
        f.close()
        lightJson = {"light":light}
        resp = jsonify(lightJson)
        resp.status_code = 200
        return resp

 @app.route('/panel')
 @support_jsonp
 def panel():
         f = open('panel.data', 'r')
         panel = int(f.readline())
         f.close()
         panelJson = {"panel":panel}
         resp = jsonify(panelJson)
         resp.status_code = 200
         return resp

if __name__ == '__main__':
        app.run(debug=True, host="192.168.1.100", port=80)
