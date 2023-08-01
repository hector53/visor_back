import pymongo
from datetime import datetime
import time
start = time.time()
# Conecta a la base de datos de MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017/")

# Selecciona la base de datos y la colección
db = client["rofex"]
collection = db["users_visor_secciones"]

buscar = collection.find({
    "id_user": "641c54920ae805d7c3df4a64"
})
#print("buscar", list(buscar))
listBuscar = list(buscar)
for x in range(len(listBuscar)):
    print("x", listBuscar[x])


