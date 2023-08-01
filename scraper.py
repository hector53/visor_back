from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
import logging
import re
logging.basicConfig(filename=f'scraper.log', level=logging.INFO,
                   format='%(asctime)s %(name)s  %(levelname)s  %(message)s  %(lineno)d ')
log = logging.getLogger(__name__)
service = Service(executable_path=r'D:\selenium\geckodriver.exe')

# Ruta del perfil de Firefox
profile_path = 'D:/firefoxprofile'
# Opciones del navegador
options = Options()
options.add_argument('-profile')
options.add_argument(profile_path)
# Activar características del navegador
options.set_preference("browser.cache.disk.enable", True)
options.set_preference("browser.cache.memory.enable", True)
options.set_preference("browser.cache.offline.enable", True)
options.set_preference("network.http.use-cache", True)
options.set_preference("browser.privatebrowsing.autostart", False)
options.set_preference("browser.download.folderList", 2)
options.set_preference("browser.download.manager.showWhenStarting", False)
driver = webdriver.Firefox(service=service, options=options, keep_alive=True)

# URL de la página que queremos acceder
url = 'https://es.tradingview.com/symbols/TVC-IBEX35/'

# Accedemos a la página utilizando el driver de Firefox
driver.get(url)
# Obtener el identificador de la ventana actual
soup = BeautifulSoup(driver.page_source, 'html.parser')
# Buscamos el script que contiene la variable auth_token
script = soup.find('script', string=re.compile('auth_token'))
if script:
    auth_token = re.search(r'auth_token":"([^"]+)"', str(script)).group(1)
    # Verificamos si se encontró el script
    print(f"auth_token encontrado: {auth_token}")
