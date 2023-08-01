from flask import Flask, jsonify, request, abort, make_response
from flask_cors import CORS
from datetime import timedelta
from datetime import datetime
from flask_jwt_extended import JWTManager, jwt_required,get_jwt_identity, unset_jwt_cookies, create_access_token
#quickfix 
from flask_pymongo import PyMongo
import logging
import time
from bson import ObjectId
import asyncio
from app.clases.webSocketServer import WebSocketServer
import gevent
from gevent import monkey
#logging.basicConfig(filename=f'reports.log', level=logging.INFO,
             #       format='%(asctime)s %(name)s  %(levelname)s  %(message)s  %(lineno)d ')
log = logging.getLogger(__name__)
app = Flask(__name__)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)
app.config["JWT_SECRET_KEY"] = "xls**/54199021Nanaas4d8asd4/7/6238742347--.@"  # Change this!
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=999999)
app.config['MONGO_URI'] = 'mongodb://localhost:27017/rofex'
jwt = JWTManager(app)
mongo = PyMongo(app)
#server = socketServer("127.0.0.1", 5353)
server = WebSocketServer("127.0.0.1", 5353)
serverSocketIniciado = False
clientsTV = {}
#socketio = SocketIO(app)
from app.request import *

