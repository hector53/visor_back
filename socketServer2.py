import asyncio
import ssl
import pathlib
import websockets
import threading

class SocketServer(threading.Thread):
    def __init__(self, host, port, ssl_cert, ssl_key):
        threading.Thread.__init__(self)
        self.host = host
        self.port = port
        self.ssl_cert = ssl_cert
        self.ssl_key = ssl_key
        self.clients = set()

    def close(self):
        # Cierra el bucle de eventos de asyncio
        asyncio.get_event_loop().stop()

    async def handle_client(self, websocket, path):
        self.clients.add(websocket)
        try:
            async for message in websocket:
                # Procesa el mensaje recibido del cliente
                await self.process_message(message)
        finally:
            # Elimina el cliente de la lista de clientes conectados
            self.clients.remove(websocket)

    async def process_message(self, message):
        # Procesa el mensaje recibido del cliente
        print("Mensaje recibido:", message)

        # Envía el mensaje a todos los clientes conectados
        await self.broadcast(message)

    async def broadcast(self, message):
        # Envía el mensaje a todos los clientes conectados
        if self.clients:
            await asyncio.wait([client.send(message) for client in self.clients])

    async def run_server(self):
        # Crea el contexto SSL
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ssl_context.load_cert_chain(certfile=self.ssl_cert, keyfile=self.ssl_key)

        # Crea el servidor WebSocket utilizando el contexto SSL
        async with websockets.serve(self.handle_client, self.host, self.port, ssl=ssl_context):
            await asyncio.Future()  # Espera a que se complete la ejecución del servidor

    def run(self):
        asyncio.set_event_loop(asyncio.new_event_loop())
        asyncio.get_event_loop().run_until_complete(self.run_server())

# Crea una instancia de SocketServer y ejecuta el servidor en un subproceso
if __name__ == "__main__":
    ssl_cert = pathlib.Path("server.crt")
    ssl_key = pathlib.Path("server.key")
    server = SocketServer(host="localhost", port=8765, ssl_cert=ssl_cert, ssl_key=ssl_key)
    server.start()