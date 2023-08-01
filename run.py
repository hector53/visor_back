from app import  app, server
import asyncio
import signal
import os
import time
# Función para manejar la señal de interrupción (Ctrl + C)
def handle_interrupt(signal, frame):
    # Detener el servidor WebSocket aquí
    # ...
    print("precionando contrl c")
    server.loop.stop()
    os._exit(0)

    # Salir de la aplicación Flask
    raise SystemExit

signal.signal(signal.SIGINT, handle_interrupt)

if __name__ == '__main__':
    server.start()
    time.sleep(2)
    app.run(host='0.0.0.0', port=5000)
