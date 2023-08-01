
import logging
import asyncio 
from app import jsonify, request, abort, make_response

log = logging.getLogger(__name__)
class SocketController:
    @staticmethod
    async def change_pairs():
        from app import server, clientsTV
        from app.clases.clientTV import clienteTV
        req_obj = request.get_json()
        client_id = req_obj["client_id"]
        pairs = req_obj["pairs"]
        #verificar que client_id este en clientsTV 
        if client_id not in clientsTV:
            #crear clienteTV
            cliente = clienteTV(client_id, server)
            cliente.pairs = pairs
            clientsTV[client_id] = cliente
            cliente.start()
            
            await asyncio.create_task(cliente.esperar_data_suscrita())
        else:
            clientsTV[client_id].pairs = pairs
            clientsTV[client_id].changing_pairs = True
            clientsTV[client_id].suscripcionCompleta = False
            await asyncio.create_task(clientsTV[client_id].esperar_data_suscrita())
        return jsonify({"status": "ok"})
    

    async def get_symbols_parents():
        from app import server, clientsTV
        from app.clases.clientTV import clienteTV
        req_obj = request.get_json()
        client_id = req_obj["client_id"]
        pairs = req_obj["pairs"]
      #  from app.clases.cla_historicotv import HistoricoTV
        #verificar que client_id este en clientsTV 
        if client_id not in clientsTV:
            #crear clienteTV
            cliente = clienteTV(client_id, server)
            cliente.pairs = pairs
            clientsTV[client_id] = cliente
            cliente.start()
            
            await asyncio.create_task(cliente.esperar_data_suscrita())
        result = clientsTV[client_id].prices
        return jsonify(result)