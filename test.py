import requests

# Define los datos de autenticación
username = "facundomartinezescoda"
password = "Faca153."

# Define la URL de inicio de sesión
login_url = "https://www.tradingview.com/accounts/signin/"

# Envía la solicitud de inicio de sesión
session = requests.Session()
response = session.post(login_url, data={"username": username, "password": password})
print("response", response.text)
#print("response.json()", response.json())
# Extrae el token de autorización de la respuesta JSON
#auth_token = response.json()["user"]["auth_token"]
#print(auth_token)