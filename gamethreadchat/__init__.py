from flask import Flask
app = Flask(__name__)

import gamethreadchat.views
from flask_sockets import Sockets
from gevent import pywsgi
from geventwebsocket.handler import WebSocketHandler

server = pywsgi.WSGIServer(('', 5000), app, handler_class = WebSocketHandler)
server.serve_forever()