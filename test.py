import re
import json

texto = """
~m~98~m~{"m":"qsd","p":["qs_mjqkbgpzthhe",{"n":"CBOT:ZSU2023","s":"ok","v":{"bid":1425.25,"ask":1425.5}}]}~m~96~m~{"m":"qsd","p":["qs_mjqkbgpzthhe",{"n":"CBOT:ZCU2023","s":"ok","v":{"bid":528.75,"ask":529.0}}]}~m~95~m~{"m":"qsd","p":["qs_mjqkbgpzthhe",{"n":"CBOT:ZCK2024","s":"ok","v":{"bid":554.5,"ask":555.0}}]}~m~98~m~{"m":"qsd","p":["qs_mjqkbgpzthhe",{"n":"CBOT:ZSF2024","s":"ok","v":{"bid":1406.25,"ask":1406.5}}]}~m~97~m~{"m":"qsd","p":["qs_mjqkbgpzthhe",{"n":"CBOT:ZCN2024","s":"ok","v":{"bid":556.25,"ask":556.75}}]}~m~98~m~{"m":"qsd","p":["qs_mjqkbgpzthhe",{"n":"CBOT:ZSH2024","s":"ok","v":{"bid":1396.5,"ask":1396.75}}]}~m~99~m~{"m":"qsd","p":["qs_mjqkbgpzthhe",{"n":"CBOT:ZSK2024","s":"ok","v":{"bid":1390.75,"ask":1391.25}}]}~m~96~m~{"m":"qsd","p":["qs_mjqkbgpzthhe",{"n":"CBOT:ZCH2024","s":"ok","v":{"bid":548.25,"ask":548.5}}]}~m~93~m~{"m":"qsd","p":["qs_mjqkbgpzthhe",{"n":"CBOT:ZC2!","s":"ok","v":{"bid":537.25,"ask":537.5}}]}~m~95~m~{"m":"qsd","p":["qs_mjqkbgpzthhe",{"n":"CBOT:ZS2!","s":"ok","v":{"bid":1406.25,"ask":1406.5}}]}~m~93~m~{"m":"qsd","p":["qs_mjqkbgpzthhe",{"n":"CBOT:ZC1!","s":"ok","v":{"bid":528.75,"ask":529.0}}]}
"""

# Definir una expresión regular para buscar los objetos JSON
patron = re.compile(r'~m~\d+~m~({.*?})')

# Buscar los objetos JSON en el texto
objetos_json = re.findall(patron, texto)

# Imprimir los objetos JSON encontrados
for objeto in objetos_json:
    print(objeto)

