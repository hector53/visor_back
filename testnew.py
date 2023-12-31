import asyncio
import websocket
from threading import Thread
import logging
from socketServer import socketServer
import json
import ssl
import re
import string
import requests
import random
from websocket import create_connection
from websocket._exceptions import WebSocketConnectionClosedException



tokenJWT = "eyJhbGciOiJSUzUxMiIsImtpZCI6IkdaeFUiLCJ0eXAiOiJKV1QifQ.eyJ1c2VyX2lkIjo0MjA3Mjc0MCwiZXhwIjoxNjg5ODkyMzc1LCJpYXQiOjE2ODk4Nzc5NzUsInBsYW4iOiJwcm9fdHJpYWwiLCJleHRfaG91cnMiOjEsInBlcm0iOiJjYm90LGNib3RfbWluaSxjbWUsY21lLWZ1bGwsY21lX21pbmksY29tZXgsY29tZXhfbWluaSxueW1leCxueW1leF9taW5pIiwic3R1ZHlfcGVybSI6InR2LXZvbHVtZWJ5cHJpY2UsdHYtY2hhcnRwYXR0ZXJucyIsIm1heF9zdHVkaWVzIjo1LCJtYXhfZnVuZGFtZW50YWxzIjowLCJtYXhfY2hhcnRzIjoyLCJtYXhfYWN0aXZlX2FsZXJ0cyI6MjAsIm1heF9zdHVkeV9vbl9zdHVkeSI6MSwibWF4X2FjdGl2ZV9wcmltaXRpdmVfYWxlcnRzIjoyMCwibWF4X2FjdGl2ZV9jb21wbGV4X2FsZXJ0cyI6MjAsIm1heF9jb25uZWN0aW9ucyI6MTB9.rHPvRsImS0mJzg8XlbM8JFnRoimt_1Hv30QIH8nccLPWDB8u_kb7qBen0jBnIAXcFNV0gebHJkWaKooHih76ZPKCJg_SDHuRdQCirq9fHw2RGmrGZI8uxQ1WVRC9ayIAgKHbcsPuXZMaEguAJizjorqRz_f0zUjORoUiRSCHcw4"
class TVSocket(Thread):
    def __init__(self, host, port):
        Thread.__init__(self)
        self.host = host
        self.port = port
        self.changing_pairs = False
        self.pairs = []
        self.log = logging.getLogger("SockerSidebar")
        self.server = socketServer(host, port, self)
        self.server.start()
        

    # Método para cerrar la conexión WebSocket de manera segura
    async def close_client_socket(self):
        # Comprueba si la conexión WebSocket está abierta antes de intentar cerrarla
        if self.ws and not self.ws.closed:
            self.ws.close()

    def generateSession(self):
        stringLength = 12
        letters = string.ascii_lowercase
        random_string = "".join(random.choice(letters) for i in range(stringLength))
        return "qs_" + random_string
    
    def search(self, exchange, symbol):
        #print(f"Searching for: {symbol} on exchange: {exchange}")  # #print the search query
        res = requests.get(
            f"https://symbol-search.tradingview.com/symbol_search/?text={symbol}&exchange={exchange}"
        )
        if res.status_code == 200:
            res = res.json()
            #print(f"Response: {res}")  # #print the response
            assert len(res) != 0, "Nothing Found."
            return res[0]
        else:
            #print("Network Error!")
            exit(1)
    
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
                
        #print(f"Symbols: {symbols}")  # #print the symbols
        return symbols
     
    def get_auth_token(self):
        sign_in_url = 'https://www.tradingview.com/accounts/signin/'
        username = 'facundomartinezescoda'
        password = 'Faca153.'
        data = {"username": username, "password": password, "remember": "on"}
        headers = {
            'Referer': 'https://www.tradingview.com'
        }
        response = requests.post(url=sign_in_url, data=data, headers=headers)
        print("response ", response.json())
        auth_token = response.json()['user']['auth_token']    
        return auth_token
    
    def suscribir_data(self,ws, pairs):
        print("suscribir_data", pairs)
        auth_token = "eyJhbGciOiJSUzUxMiIsImtpZCI6IkdaeFUiLCJ0eXAiOiJKV1QifQ.eyJ1c2VyX2lkIjo0MjA3Mjc0MCwiZXhwIjoxNjg5OTY3Mzc4LCJpYXQiOjE2ODk5NTI5NzgsInBsYW4iOiJwcm9fdHJpYWwiLCJleHRfaG91cnMiOjEsInBlcm0iOiJjYm90LGNib3RfbWluaSxjbWUsY21lLWZ1bGwsY21lX21pbmksY29tZXgsY29tZXhfbWluaSxueW1leCxueW1leF9taW5pIiwic3R1ZHlfcGVybSI6InR2LXZvbHVtZWJ5cHJpY2UsdHYtY2hhcnRwYXR0ZXJucyIsIm1heF9zdHVkaWVzIjo1LCJtYXhfZnVuZGFtZW50YWxzIjowLCJtYXhfY2hhcnRzIjoyLCJtYXhfYWN0aXZlX2FsZXJ0cyI6MjAsIm1heF9zdHVkeV9vbl9zdHVkeSI6MSwibWF4X2FjdGl2ZV9wcmltaXRpdmVfYWxlcnRzIjoyMCwibWF4X2FjdGl2ZV9jb21wbGV4X2FsZXJ0cyI6MjAsIm1heF9jb25uZWN0aW9ucyI6MTB9.lethKqmukZTrnoTr6dx6UmIkdPFHs3XTAqAZomFTmma7IcSSBLldvCsIxANk3AnTRUuHecCX-KlxDOEpm9qcZ3XMjuenVyr7CL03OQv5zbI04_0pMCkmQwGmZLxdPTRBPpEKf3ZmRt_0TsUJwGB3dOFZxXomoXbfhXxzPBZdbvI"
        self.sendMessage(ws, "set_auth_token", [auth_token])
        session = self.generateSession()
        self.sendMessage(ws, "quote_create_session", [session])
        self.sendMessage(ws, "quote_set_fields", [session, 'base-currency-logoid', 'ch', 'chp', 'currency-logoid', 'currency_code', 'current_session', 'description', 'exchange', 'format', 'fractional', 'is_tradable', 'language', 'local_description', 'logoid', 'lp', 'lp_time', 'minmov', 'minmove2', 'original_name', 'pricescale', 'pro_name', 'short_name', 'type', 'update_mode', 'volume', 'ask', 'bid', 'fundamentals', 'high_price', 'low_price', 'open_price', 'prev_close_price', 'rch', 'rchp', 'rtc', 'rtc_time', 'status', 'industry', 'basic_eps_net_income', 'beta_1_year', 'market_cap_basic', 'earnings_per_share_basic_ttm', 'price_earnings_ttm', 'sector', 'dividends_yield', 'timezone', 'country_code', 'provider_id']) 
        # For each pair, get all the symbols (including contracts) and add them to the session
        for i, pair in enumerate(pairs):
           # print("pair", pair)
            # Split the pair into exchange and symbol
            exchange, symbol = pair.split(':')
            # Search for the symbol in the specified market category
            data = self.search(exchange, symbol)
            # Get all the symbol IDs from the response
            symbol_ids = self.getSymbolId(data)
            # Add all the symbols to the session
            for symbol_id in symbol_ids:
               # print("symbol_id", symbol_id)
                self.sendMessage(ws, "quote_add_symbols", [session, symbol_id])
        print("saliendo de suscribir data")

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
    
    def prependHeader(self, st):
        return "~m~" + str(len(st)) + "~m~" + st

    def constructMessage(self, func, paramList):
        return json.dumps({"m": func, "p": paramList}, separators=(",", ":"))

    def createMessage(self, func, paramList):
        return self.prependHeader(self.constructMessage(func, paramList))

    def sendMessage(self, ws, func, args):
        ws.send(self.createMessage(func, args))

    def process_message(self, msg):
        try:
         #   jsonRes = json.loads(msg)
           # print(f"Mensaje recibido: {jsonRes}")
            self.server.broadcast(json.dumps(msg))
           
        except json.JSONDecodeError:
            print(f"Failed to decode JSON message.")
        except KeyError:
            print(f"Key 'm' not found in price message.")
    
    # Método para hacer un update de pairs desde el cliente
    def update_pairs(self, message):
        # Intenta decodificar el mensaje. Si falla, regresa inmediatamente.
        try:
            message_data = json.loads(message)
        except json.JSONDecodeError:
            return

        # Si el mensaje no contiene la clave 'pairs', regresa inmediatamente.
        if 'pairs' not in message_data:
            return

        # El mensaje es relevante, procede como de costumbre.
        print("update_pairs, pasando variable a true")
        self.changing_pairs = True
        self.pairs = message_data["pairs"]
        print("Cambiando pairs")

    async def run_client_socket(self):
        print("entrando al run client socket")
        prices = {}  
        tokenNuevo = "eyJhbGciOiJSUzUxMiIsImtpZCI6IkdaeFUiLCJ0eXAiOiJKV1QifQ.eyJ1c2VyX2lkIjo0MjA3Mjc0MCwiZXhwIjoxNjg5ODkyNDYwLCJpYXQiOjE2ODk4NzgwNjAsInBsYW4iOiJwcm9fdHJpYWwiLCJleHRfaG91cnMiOjEsInBlcm0iOiJjYm90LGNib3RfbWluaSxjbWUsY21lLWZ1bGwsY21lX21pbmksY29tZXgsY29tZXhfbWluaSxueW1leCxueW1leF9taW5pIiwic3R1ZHlfcGVybSI6InR2LWNoYXJ0cGF0dGVybnMsdHYtdm9sdW1lYnlwcmljZSIsIm1heF9zdHVkaWVzIjo1LCJtYXhfZnVuZGFtZW50YWxzIjowLCJtYXhfY2hhcnRzIjoyLCJtYXhfYWN0aXZlX2FsZXJ0cyI6MjAsIm1heF9zdHVkeV9vbl9zdHVkeSI6MSwibWF4X2FjdGl2ZV9wcmltaXRpdmVfYWxlcnRzIjoyMCwibWF4X2FjdGl2ZV9jb21wbGV4X2FsZXJ0cyI6MjAsIm1heF9jb25uZWN0aW9ucyI6MTB9.SuRfZT8p1JbaurZwSsnxrTD0vhlrBbpbizrq90n68aDxNOMQl_zXjAj5De52qWOuQOCYQMPJ6XYht7o9xLMFQ9QoGvHSARys9ENlNpJrV-TSBAt3WaasV6Cz0KGCVtWnm7cTfs1Pn--fIHRU_FZ8VWzRllQ_sVE6hbj-jP9cUaM"
        while True:
            try:
                # Crear una conexión WebSocket segura utilizando la función create_connection
                if self.changing_pairs==True:
                    print("cambiando pairs pasando a false la variable")
                    self.changing_pairs=False
                ws = self.create_websocket_connection()
                self.suscribir_data(ws,self.pairs)
                # Recibir mensajes del servidor

                try:
                    while self.changing_pairs==False:
                     #   print("escuchando")
                        result = ws.recv()
                       # print("result-------------------------------------------------------", result)
                        try: 
                            patron = re.compile(r'~m~\d+~m~({.*?})')
                            # Buscar los objetos JSON en el texto
                            objetos_json = re.findall(patron, result)
                            self.process_message(objetos_json)
                        except Exception as e:
                            print("error con el patron ")
                     
                    print("saliendo del ciclo infinito q escucha")
                    ws.close()
                    prices = {}
                except Exception as e:
                    ws.close()
                    print("error en el ciclo infinito q escucha")

            except Exception as e:
                print("Error: " + str(e))
                print("Reconnecting in 5 seconds...")
                await asyncio.sleep(5)

async def main():
    client = TVSocket("127.0.0.1", 5353)
    pairs = ["CBOT:ZS","CBOT:ZC","CBOT:ZW", "MATBAROFEX:SOJ.ROS","MATBAROFEX:MAI.ROS","MATBAROFEX:TRI.ROS",  "SP:SPX", "NASDAQ:NDX",  "NYMEX:CL1!", "COMEX:GC1!"]
    client.pairs = pairs
  #  print("pairs", client.pairs)
    try:
        await client.run_client_socket()
    except KeyboardInterrupt:
        client.server.close()
    print("terminado todo")


if __name__ == "__main__":
    asyncio.run(main())