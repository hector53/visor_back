import asyncio
import websockets
from urllib.parse import urlparse, parse_qs
from threading import Thread
import logging
import time
class WebSocketServer(Thread):
    def __init__(self, host, port):
        Thread.__init__(self)
        """
        Constructor de la clase WebSocketServer.
        Args:
        - host (str): dirección IP o nombre de host donde se alojará el servidor.
        - port (int): número de puerto donde se alojará el servidor.
        """
        self.log = logging.getLogger(f"websocketServer")
        self.host = host
        self.port = port
        self.clients = {}
        self.clientsFront = {}
      #  self.socketMessages = socketMessages
        self.loop = None
        self.last_ping_times = {}

    def run(self):
        """
        Inicia el servidor WebSocket.
        """
        print("start cola")
        loop = asyncio.new_event_loop()# creo un nuevo evento para asyncio y asi ejecutar todo de aqui en adelante con async await 
        self.loop = loop
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.run_forever())#ejecuto la funcion q quiero
        loop.close()#cierro el evento

    async def handle(self, websocket, path):
        
        """
        Manejador de solicitudes de WebSocket.

        Args:
        - websocket (WebSocketServerProtocol): objeto que representa la conexión WebSocket.
        - path (str): ruta de la solicitud WebSocket.

        Nota:
        - Esta función se ejecuta cada vez que se recibe una solicitud WebSocket.
        """
        # Acceder a los parámetros de la URL de la solicitud de WebSocket
        query = urlparse(path).query
        params = parse_qs(query)
        client_id = params.get('client_id', [None])[0]
        isClientFront=0
        front = params.get('front', [None])[0]
        if front:
            isClientFront = 1
        if isClientFront==1:
            self.clientsFront[client_id] = websocket
        print(f"Nuevo cliente conectado con ID {client_id}")

        # Agregar el cliente a la lista de clientes
        self.clients[client_id] = websocket

        try:
            async for message in websocket:
                self.log.info(f"mensaje recibido de cliente con ID {client_id}: {message}")
                print(f"Mensaje recibido de cliente con ID {client_id}: {message}")
                # Actualizar el tiempo del último ping recibido para el cliente actual
                self.last_ping_times[client_id] = time.time()
                # enviar a procesar el mensaje en una tarea aparte para no bloquear el hilo principal
             #   asyncio.create_task(self.socketMessages.process_message(message))
               # await websocket.send(message)
        except Exception:
            print(f"Cliente con ID {client_id} desconectado")
            
            
    async def check_heartbeat(self):
        print("entrando a check heartbeat")
        from app import clientsTV
        while True:
        #    print("check hearbeta")
            # Verificar el estado de cada cliente
            for client_id, last_ping_time in self.last_ping_times.items():
                print("revisando time del cliente: ", client_id)
                # Verificar si ha pasado más de 30 segundos desde el último ping recibido
                if time.time() - last_ping_time > 30:
                    # Desconectar al cliente
                    # ...
                    # Por ejemplo:
                    websocket = self.clients[client_id]
                    if not websocket.closed:
                        await websocket.close()
                    print(f"Cliente con ID {client_id} desconectado por inactividad")
                    del self.last_ping_times[client_id]
                    del self.clients[client_id]
                    if client_id in self.clientsFront:
                        del self.clientsFront[client_id]
                    #pasar variable closeThread para detener el thread de este cliente 
                    print("vamos a ver q pasa con clientsTv")
                    print("clientsTV", clientsTV)
                    clientsTV[client_id].changing_pairs = True
                    clientsTV[client_id].closeThread = True
                    clientsTV[client_id].join()
                    del clientsTV[client_id]
                    print("cliente desconectado y cerrado su thread correctamente ")
                    print("clientsTV", clientsTV)
                    break
                    # Eliminar el cliente de la lista de clientes

            # Esperar antes de volver a verificar
            await asyncio.sleep(1)  # Intervalo de verificación de 1 segundo

    async def send_message(self, client_id, message):
       # print("entrando a enviar mensaje")
        """
        Enviar un mensaje a un cliente específico por medio de su ID.

        Args:
        - client_id (str): ID del cliente al que se le enviará el mensaje.
        - message (str): mensaje que se enviará al cliente.

        Nota:
        - Si el cliente no está conectado, el mensaje no se enviará.
        """
        # Enviar un mensaje a un cliente específico por medio de su ID
        websocket = self.clients.get(client_id)
        if websocket:
           # print("si hay cliente con id")
          #  print("enviar mensaje")
            await websocket.send(message)

    async def broadcast_message(self, message):
        """
        Enviar un mensaje a todos los clientes conectados.

        Args:
        - message (str): mensaje que se enviará a todos los clientes.
        """
        # Enviar un mensaje a todos los clientes conectados
        for websocket in self.clients.values():
            await websocket.send(message)

    def send_message_not_await(self, client_id, message):
        from app import clientsTV
       # print("entrando a send_message_not_await ")
        """
        Enviar un mensaje a un cliente específico por medio de su ID.

        Args:
        - client_id (str): ID del cliente al que se le enviará el mensaje.
        - message (str): mensaje que se enviará al cliente.

        Nota:
        - Si el cliente no está conectado, el mensaje no se enviará.
        """
        # Enviar un mensaje a un cliente específico por medio de su ID
        websocket = self.clients.get(client_id)
       # print("despues de websocket ", websocket)
        if websocket:
            try:
            #    print("enviando call soon")
                if not websocket.closed:
                    self.loop.call_soon_threadsafe(asyncio.ensure_future, websocket.send(message))
                else:
                    print("el cliente ya se desconecto ", client_id)
                    
            except Exception as e:
                print("error al enviar mensaje a cliente con id: ", client_id, e)

    def broadcast_not_await_front(self, message):
        """
        Enviar un mensaje a todos los clientes conectados.

        Args:
        - message (str): mensaje que se enviará a todos los clientes.
        """
        # Enviar un mensaje a todos los clientes conectados
        for websocket in self.clientsFront.values():
            self.loop.call_soon_threadsafe(asyncio.ensure_future, websocket.send(message))

    async def run_forever(self):
        """
        Ejecutar el servidor WebSocket de forma indefinida.
        """
        asyncio.create_task(self.check_heartbeat())
        async with websockets.serve(self.handle, self.host, self.port):
            await asyncio.Future()  # Esperar indefinidamente