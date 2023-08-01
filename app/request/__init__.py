from app import app
import logging
log = logging.getLogger("requests")
#controllers 
from app.controllers import *


###user####
app.add_url_rule('/api/checkToken', view_func=UserController.checkToken,   methods=['POST'])
app.add_url_rule('/api/logout', view_func=UserController.logout,   methods=['POST'])
app.add_url_rule('/api/login', view_func=UserController.login,   methods=['POST'])
app.add_url_rule('/api/get_historico_visor', view_func=UserController.historico_visor, methods=['POST'] )
app.add_url_rule('/api/get_news', view_func=UserController.get_news, methods=['POST'] )


###secciones###
app.add_url_rule('/api/get_secciones_visor/<string:id>', view_func=SeccionesController.get_secciones_visor, methods=['POST'] )
app.add_url_rule('/api/secciones/<string:id_user>', view_func=SeccionesController.edit_secciones, methods=['PUT'] )
app.add_url_rule('/api/seccion/<string:id>', view_func=SeccionesController.edit_seccion, methods=['PUT'] )
app.add_url_rule('/api/seccion/<string:id_user>', view_func=SeccionesController.add_seccion, methods=['POST'] )
app.add_url_rule('/api/seccion/<string:id>', view_func=SeccionesController.delete_seccion, methods=['DELETE'] )
###socket####

app.add_url_rule('/api/get_symbols_parents', view_func=SocketController.get_symbols_parents, methods=['POST'] )
app.add_url_rule('/api/change_pairs', view_func=SocketController.change_pairs, methods=['POST'] )