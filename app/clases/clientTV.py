import json
import random
import string
import ssl
import requests
from websocket import create_connection
import logging
import asyncio
from threading import Thread
import time
from app.clases.webSocketServer import WebSocketServer
class clienteTV(Thread):
    def __init__(self, client_id, server:WebSocketServer):
        Thread.__init__(self)
        self.client_id = client_id
        self.log = logging.getLogger(f"clientTV_{client_id}")
        self.prices = {}
        self.changing_pairs = False
        self.threadSymbols = None
        self.dataSuscrita = []
        self.pairs = []
        self.suscripcionCompleta = False
        self.server = server
        self.closeThread = False

    def search(self, exchange, symbol):
        res = requests.get(
            f"https://symbol-search.tradingview.com/symbol_search/?text={symbol}&exchange={exchange}"
        )
        if res.status_code == 200:
            res = res.json()
         #   print(f"Response: {res}")  # Print the response
            assert len(res) != 0, "Nothing Found."
            return res[0]
        else:
            print("Network Error!")
            exit(1)

    def get_auth_token(self):
        sign_in_url = 'https://www.tradingview.com/accounts/signin/'
        username = ''
        password = ''
        data = {"username": username, "password": password, "remember": "on"}
        headers = {
            'Referer': 'https://www.tradingview.com'
        }
        response = requests.post(url=sign_in_url, data=data, headers=headers)
        auth_token = response.json()['user']['auth_token']    
        return auth_token
    
    def create_websocket_connection(self):
        # create tunnel
        tradingViewSocket = "wss://prodata.tradingview.com/socket.io/websocket" #'wss://data.tradingview.com/socket.io/websocket?from=chart/DZ1tUo5u/&date=XXXX_XX_XX-XX_XX'
        headers = json.dumps({"Origin": "https://www.tradingview.com", "Accept-Encoding": "gzip, deflate, br", 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'})

        # Add these two lines to create a context that doesn't check the SSL certificate
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

        ws = create_connection(tradingViewSocket, header=headers, sslopt={"cert_reqs": ssl.CERT_NONE, "check_hostname": False})
        return ws
    
    def generateSession(self):
        stringLength = 12
        letters = string.ascii_lowercase
        random_string = "".join(random.choice(letters) for i in range(stringLength))
        return "qs_" + random_string

    def chartSession(self):
        stringLength = 12
        letters = string.ascii_lowercase
        random_string = "".join(random.choice(letters) for i in range(stringLength))
        return "cs_" + random_string
    
    def prependHeader(self, st):
        return "~m~" + str(len(st)) + "~m~" + st

    def constructMessage(self, func, paramList):
        return json.dumps({"m": func, "p": paramList}, separators=(",", ":"))
    
    def createMessage(self, func, paramList):
        return self.prependHeader(self.constructMessage(func, paramList))

    def sendMessage(self, ws, func, args):
        #start_time = time.time()  # Registra el tiempo antes de enviar el mensaje
        ws.send(self.createMessage(func, args))

    def getSymbolId(self, data):
        # Here data is the whole response from search()
        symbols = []
        
        # Check if the 'contracts' key exists and has elements
        if 'contracts' in data and len(data['contracts']) > 0:
            # If it does, get all the contracts and append them to the symbols list
            for contract in data['contracts']:
                symbols.append(f"{data['exchange'].upper()}:{contract['symbol'].upper()}")
        else:
            # If there are no contracts, just get the 'symbol' key
            symbols.append(f"{data['exchange'].upper()}:{data['symbol'].upper()}")
                
       # print(f"Symbols: {symbols}")  # Print the symbols
        return symbols
    
    def suscribir_data(self,ws):
        print("suscribir_data", self.pairs)
        auth_token = "eyJhbGciOiJSUzUxMiIsImtpZCI6IkdaeFUiLCJ0eXAiOiJKV1QifQ.eyJ1c2VyX2lkIjo0MjA3Mjc0MCwiZXhwIjoxNjg5OTY3Mzc4LCJpYXQiOjE2ODk5NTI5NzgsInBsYW4iOiJwcm9fdHJpYWwiLCJleHRfaG91cnMiOjEsInBlcm0iOiJjYm90LGNib3RfbWluaSxjbWUsY21lLWZ1bGwsY21lX21pbmksY29tZXgsY29tZXhfbWluaSxueW1leCxueW1leF9taW5pIiwic3R1ZHlfcGVybSI6InR2LXZvbHVtZWJ5cHJpY2UsdHYtY2hhcnRwYXR0ZXJucyIsIm1heF9zdHVkaWVzIjo1LCJtYXhfZnVuZGFtZW50YWxzIjowLCJtYXhfY2hhcnRzIjoyLCJtYXhfYWN0aXZlX2FsZXJ0cyI6MjAsIm1heF9zdHVkeV9vbl9zdHVkeSI6MSwibWF4X2FjdGl2ZV9wcmltaXRpdmVfYWxlcnRzIjoyMCwibWF4X2FjdGl2ZV9jb21wbGV4X2FsZXJ0cyI6MjAsIm1heF9jb25uZWN0aW9ucyI6MTB9.lethKqmukZTrnoTr6dx6UmIkdPFHs3XTAqAZomFTmma7IcSSBLldvCsIxANk3AnTRUuHecCX-KlxDOEpm9qcZ3XMjuenVyr7CL03OQv5zbI04_0pMCkmQwGmZLxdPTRBPpEKf3ZmRt_0TsUJwGB3dOFZxXomoXbfhXxzPBZdbvI"
        self.sendMessage(ws, "set_auth_token", [auth_token])
        session = self.generateSession()
        self.sendMessage(ws, "quote_create_session", [session])
        self.sendMessage(ws, "quote_set_fields", [session,  'ch', 'chp',  'exchange',  'lp',    'original_name',  'volume', 'ask', 'bid']) 
        # For each pair, get all the symbols (including contracts) and add them to the session
        for i, pair in enumerate(self.pairs):
           # print("pair", pair)
            # Split the pair into exchange and symbol
            exchange, symbol = pair.split(':')
            # Search for the symbol in the specified market category
            data = self.search(exchange, symbol)
            # Get all the symbol IDs from the response
            symbol_ids = self.getSymbolId(data)
            # Add all the symbols to the session
            for symbol_id in symbol_ids:
              #  print("symbol_id", symbol_id)
                self.sendMessage(ws, "quote_add_symbols", [session, symbol_id])
                if self.suscripcionCompleta==False:
                    self.dataSuscrita.append(symbol_id)
                  
        print("saliendo de suscribir data")
    
    async def borrar_symbol_suscrito(self, symbol):
       # print("borrar_symbol_suscrito", symbol, self.dataSuscrita)
        try:
            if symbol in self.dataSuscrita:
                #quiero recorrer todas las keys de este simbolo para ver si tienen valores distintos de 0
                #si todas tienen valores distintos de 0 la borro de resto no la borro
                if len(self.dataSuscrita)==1:
                        self.dataSuscrita = []
                        print("paso suscripcion a 0")
                        self.suscripcionCompleta = True
                        print("espero 2 seg")
                        await asyncio.sleep(2)
                else:
                    self.dataSuscrita.remove(symbol)
                

                """
                contadorKeysNot0 = 0
                print("entro a borrar el ultimo simbolo")
                for key in self.prices[symbol]:
                    if self.prices[symbol][key] != 0:
                        contadorKeysNot0+=1
                
                if contadorKeysNot0 == 6:
                """
                    
                print("saliendo de borrar el ultimo simbolo")
        except Exception as e:
            print("error borrando symbol: ", e)


    async def process_message(self, msg):
        try:
            jsonRes = json.loads(msg)
        #    print("jsonRes", jsonRes)
            if jsonRes["m"] == "qsd":
                try:
                    symbol = jsonRes["p"][1]["n"]
                    keys = ["lp", "bid", "ask", "ch", "chp", "volume"]
                    if symbol not in self.prices:
                        self.prices[symbol] = {}
                    for key in keys:
                        value = jsonRes["p"][1]["v"].get(key)
                        if value is not None:
                            self.prices[symbol][key] = value
                    if len(self.dataSuscrita)>0:
                    #    print("es mayor a cero asi q mando a borrar")
                        await self.borrar_symbol_suscrito(symbol)
                    else:
                       # print("ya mande a borrar todos asi que mando a enviar y paso suscripcion completa a true")
                        if self.changing_pairs==False:
                           # print("mando a enviar")
                            self.server.send_message_not_await(self.client_id, json.dumps(jsonRes["p"][1]))
                      
                   # print("precios",json.dumps(self.prices))
              #      self.server.broadcast(json.dumps(prices))
                except KeyError:
                    print("Could not find key in message:")
        except Exception as e:
            print(f"Failed to decode JSON message.", e)
  

    async def esperar_symbols_parents(self):
        #hacer un while que espere 5 seg y que pase la variable self.changin_pairs a true luego de los 5 seg
        print("esperar_symbols_parents")
        await asyncio.sleep(10)
       # self.changing_pairs = True
        print("pasaron los 5 seg")

    async def get_symbols_parents_childs(self, pairs):
        print("get_symbols_parents_childs")
        self.prices = {}
        self.changing_pairs = False
        
        # Crear una conexión WebSocket segura utilizando la función create_connection
        ws = self.create_websocket_connection()
        await self.suscribir_data(ws,pairs)
    #    asyncio.create_task(self.esperar_symbols_parents())
        # Recibir mensajes del servidor
        try:
            while self.changing_pairs==False:
                #   print("escuchando")
                result = ws.recv()
                messages = result.split("~m~")
                messages = [msg for msg in messages if msg]
                for msg in messages:
                    # print("msg", msg)
                    if msg.startswith("{"):
                        # print("msg", msg)
                        #start_time = time.time()
                        await self.process_message(msg)
                #   print("result", result)
                await asyncio.sleep(0.1)
          #  print("saliendo del ciclo infinito q escucha")
            ws.close()
        except Exception as e:
            ws.close()
            print("error en el ciclo infinito q escucha")
        print("retornando precios")
        return self.prices


    async def get_data_for_symbol(self, pairs, limit):
        ws = self.create_websocket_connection()
        contador = 0
        try:
            session = self.generateSession()
            print("session: ",session)

            self.sendMessage(ws, "quote_create_session", [session])
            print("Sent quote_create_session")

           
            # For each pair, get all the symbols (including contracts) and add them to the session
            for i, pair in enumerate(pairs):
                # Generate a unique symbol name for this pair
                symbol_name = f"sds_sym_{i+1}"

                # No need to search pair from specified market category, using pair as symbol_id directly
                symbol_id = pair.upper()
                self.sendMessage(ws, "quote_add_symbols", [session, symbol_id])
                print(f"Sent quote_add_symbols with {symbol_id}")

                # generate new chart session for each pair
                chart = self.chartSession()
                print("chart ",chart)

                # create new chart session for each pair
                self.sendMessage(ws, "chart_create_session", [chart, ""])  
                print("Sent chart_create_session")

                self.sendMessage(ws, "resolve_symbol", [chart, symbol_name, symbol_id])
                print(f"Sent resolve_symbol with {symbol_id}")

                self.sendMessage(ws, "create_series", [chart, f"sds_{i+1}", f"s{i+1}", symbol_name, "1D", limit, ""])
                print("Sent historical")
                print("se acabaron los simbolos")
            print("se acabaron los pairs")
            response = await self.escuchar_socket(ws, pair)
            # Start receiving historical data
            return response

        except Exception as e:
            print(f"ERROR: {e}")
    async def escuchar_socket(self, ws, pair):
        try:
            response = {}
            r = False
            while True:
                print("ciclo infinito")
                result = ws.recv()
               # self.log.info(f"result: {result}")
                messages = result.split("~m~")
                messages = [msg for msg in messages if msg]

                for msg in messages:
                    if msg.startswith("{"):
                        res, result = self.process_history_message(msg, pair)
                        if res:
                            response = result 
                            r = True
                            print("WebSocket connection closed.")
                            break 
                if r:
                    break
                
            return response
        except KeyboardInterrupt:
            print("\nGoodbye!")
            return None

    def process_history_message(self, msg,pair):
       # log.info(f"llego mensaje de socket pair: {pair} :{msg} ")
        try:
            json_res = json.loads(msg)
            if json_res["m"] == "timescale_update":
                if "sds_1" in json_res["p"][1]:  # If the 'sds_1' key exists in the message. "s" trae la data
                    historical_data = json_res["p"][1]["sds_1"]["s"]
                    formatted_data = self.format_historical_data(historical_data)
                    return True, formatted_data
            return False, {}
        except json.JSONDecodeError:
            print(f"Failed to decode JSON message: {msg}")
            return False, {}
        except KeyError:
            print(f"Key 'm' not found in history message: {json_res}")
            return False, {}
        
    def format_historical_data(self, historical_data):
        formatted_data = []
        for data in historical_data:
            record = {
                "Timestamp": data['v'][0],
                "Open": data['v'][1],
                "High": data['v'][2],
                "Low": data['v'][3],
                "Close": data['v'][4]
            }
            # Check if 'Volume' exists
            if len(data['v']) > 5:
                record["Volume"] = data['v'][5]
            formatted_data.append(record)
        
        return formatted_data
    
    async def esperar_data_suscrita(self):
        print("esperar_data_suscrita")
        while True:
            if self.suscripcionCompleta:
                print("se borraron todos los simbolos")
                break
            await asyncio.sleep(0.01)
        print("pasaron los 5 seg")
        return self.prices
    
    def run(self):
        """
        Inicia el servidor WebSocket.
        """
        print("start cola")
        loop = asyncio.new_event_loop()# creo un nuevo evento para asyncio y asi ejecutar todo de aqui en adelante con async await 
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.run_forever())#ejecuto la funcion q quiero
        loop.close()#cierro el evento
    
    async def run_forever(self):
        print("entrando a run")
        while self.closeThread==False:
            try:
                # Crear una conexión WebSocket segura utilizando la función create_connection
                if self.changing_pairs==True:
                    print("cambiando pairs pasando a false la variable")
                    self.changing_pairs=False
                ws = self.create_websocket_connection()
                self.suscribir_data(ws)
                # Recibir mensajes del servidor
                try:
                    while self.changing_pairs==False:
                        result = ws.recv()
                        messages = result.split("~m~")
                        messages = [msg for msg in messages if msg]
                        for msg in messages:
                            if msg.startswith("{"):
                                await self.process_message(msg)
                    print("saliendo del ciclo infinito q escucha")
                    ws.close()
                except Exception as e:
                    ws.close()
                    print("error en el ciclo infinito q escucha")

            except Exception as e:
                print("Error: " + str(e))
                print("Reconnecting in 5 seconds...")
                await asyncio.sleep(5)