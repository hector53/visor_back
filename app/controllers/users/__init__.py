from app import jsonify, request, abort, make_response
from app import  jwt_required,get_jwt_identity, unset_jwt_cookies, create_access_token
from app import  logging, mongo
from app.modulos_db import getDataOne
import asyncio
import requests
log = logging.getLogger(__name__)
class UserController:
    @staticmethod

    @jwt_required()
    def checkToken():
        print("checktoken ")
        user = get_jwt_identity()
        print("user", user)
        return jsonify({
            "status": "success",
            "user": user
        })
    
    @jwt_required()
    def logout():
        body = request.get_json()
        print("logout ")
        token = get_jwt_identity()
        # Eliminar las cookies de JWT para remover el token del cliente
        response = jsonify({'message': 'Logout exitoso', 'status': "success"})
        unset_jwt_cookies(response)
        return response, 200
    
    async def get_news_request(pairs):
        symbols_news = pairs
        news = []
        headers = {
        'Origin': 'https://www.tradingview.com', "Accept-Encoding": "gzip, deflate, br", 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
        for symbol in symbols_news:
            url = f'https://news-headlines.tradingview.com/headlines/?category=futures&lang=en&symbol={symbol}'
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                filtered_news = [item for item in response.json() if any(
                s in symbols_news for s in [s['symbol'] for s in item.get('relatedSymbols', [])])]
                news += filtered_news
        return news
    
    async def get_secciones_visor(id):
        print("el user con id", id, "pide secciones")
        try:
            seccionesUser = mongo.db.users_visor_secciones.find({"id_user": id})
            
            results_list = list(seccionesUser)
            print("results_list", results_list)
            if seccionesUser:
                print("si tiene secciones es te user ")
                # Convertir el cursor en una lista y convertir los ObjectId a str
                for x in range(len(results_list)):
                    print("recorriendo el ciclo x")
                    results_list[x]["_id"] = str(results_list[x]["_id"])
            return jsonify(results_list)
        except Exception as e:
            print("error", e)
            return jsonify([])

    
    async def get_news():
        req_obj = request.get_json()
        symbols = req_obj["symbols"]
        news = await UserController.get_news_request(symbols); 
        return jsonify(news)
    
    async def historico_visor():
        from app.clases.cla_historicotv import HistoricoTV
        req_obj = request.get_json()
        symbol = req_obj["symbol"]
        limit = req_obj["limit"]
        pairs = []
        pairs.append(symbol)
        his = HistoricoTV()
        result = await asyncio.create_task(his.get_data_for_symbol(pairs, limit))
       # print("result result", result)
        return jsonify(result)
    
    async def get_symbols_parents():
        from app.clases.cla_historicotv import HistoricoTV
        req_obj = request.get_json()
        pairs = req_obj["pairs"]
        his = HistoricoTV()
        result = await asyncio.create_task(his.get_symbols_parents_childs(pairs))
       # print("result result", result)
        return jsonify(result)
    
    def login():
        body = request.get_json()
        print(body)
        try: 
            username = str(body["username"])
            password = str(body["password"])
            print("username", username)
            print("password", password)
            user = mongo.db.users.find_one_or_404({'username': username, 'password': password})
            print("voy por aqui en el login")
            print("user", user)
            user["_id"] = str(user["_id"])
            if user:
                print("user", user)
            # El usuario existe
                print('El usuario existe')  
                access_token = create_access_token(identity=user)
                response = {
                    'status': True,
                    'message': 'Login successful',
                    'token': access_token,
                }
                return jsonify(response)
            else:
            # El usuario no existe
                abort(make_response(jsonify(message="el usuario no existe"), 401))
        except Exception as e: 
            log.error(f"error en login: {e}")
            abort(make_response(jsonify(message=f"error: {e}"), 401))