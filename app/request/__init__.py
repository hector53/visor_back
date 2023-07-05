from app import app
#controllers 
from app.controllers import *

###user####
app.add_url_rule('/api/checkToken', view_func=UserController.checkToken,   methods=['POST'])
app.add_url_rule('/api/logout', view_func=UserController.logout,   methods=['POST'])
app.add_url_rule('/api/login', view_func=UserController.login,   methods=['POST'])
app.add_url_rule('/api/get_historico_visor', view_func=UserController.historico_visor, methods=['POST'] )
app.add_url_rule('/api/get_news', view_func=UserController.get_news, methods=['POST'] )