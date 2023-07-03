from app import jsonify, request, abort, make_response
from app import  jwt_required,get_jwt_identity, unset_jwt_cookies, create_access_token
from app import  logging
from app.modulos_db import getDataOne
import asyncio
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
    
    def login():
        body = request.get_json()
        print(body)
        try: 
            username = body["username"]
            password = body["password"]
            sql = f"SELECT * FROM users where username =  %s and password =%s "
            tupla = (username, password)
            user = getDataOne(sql, tupla)
            if user:
                print("user", user)
                userData = {
                    "id": user[0],
                    "username":user[1]
                }
            # El usuario existe
                print('El usuario existe')  
                access_token = create_access_token(identity=userData)
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