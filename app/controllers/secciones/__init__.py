import logging
import asyncio 
from app import jsonify, request, abort, make_response, mongo, ObjectId

log = logging.getLogger(__name__)
class SeccionesController:
    @staticmethod
    async def get_secciones_visor(id):
        print("el user con id", id, "pide secciones")
        try:
            seccionesUser = mongo.db.users_visor_secciones.find_one({"id_user": id}, {"_id": 0})
            print("seccionesUserrrrrrrrrrr", seccionesUser)
            return jsonify(seccionesUser)
        except Exception as e:
            print("error", e)
            return jsonify([])
        
    async def edit_secciones(id_user):
        print("edit seccion")
        body = request.get_json()
        print("body", body)
        #ahora actualizar en mongo.db.users_visor_secciones
        """
        body = [{'_id': '64c4245123e6bdc3880b114f', 'cols': 6, 'componentes': [{'author': 'Héctor Acosta', 'description': 'test component descripcion', 'id': 'test-component', 'name': 'test Component', 'version': '1.0.0'}, {'author': 'Héctor Acosta', 'description': 'test component descripcion', 'id': 'test-component', 'name': 'test Component', 'version': '1.0.0'}], 'id_user': '641c54920ae805d7c3df4a64', 'name': 'SeccionNueva', 'position': 1}, {'_id': '64c425c723e6bdc3880b1151', 'cols': 12, 'componentes': [{'author': 'Héctor Acosta', 'description': 'test component descripcion', 'id': 'test-component', 'name': 'test Component', 'version': '1.0.0'}], 'id_user': '641c54920ae805d7c3df4a64', 'name': 'Mercados', 'position': 2}]
        """
        try:
            getSeccionesUser = mongo.db.users_visor_secciones.find_one({"id_user": id_user})
            if getSeccionesUser:
                mongo.db.users_visor_secciones.update_one(
                        {"id_user": id_user},
                        {"$set": {
                            "secciones": body["secciones"],
                            "pairs": body["pairs"]
                        }}
                    )
            else:
                mongo.db.users_visor_secciones.insert_one(
                    {
                        "id_user": id_user,
                        "secciones": body["secciones"],
                        "pairs": body["pairs"]
                    }
                )
        except Exception as e:
            print("error", e)
            return jsonify({"status": "error"})
        return jsonify({"status": "ok"})
        
    async def edit_seccion(id):
        print("edit seccion")
        body = request.get_json()
        print("body", body)
        #ahora actualizar en mongo.db.users_visor_secciones
        try:
            del body["_id"]
            print("body2", body)
            mongo.db.users_visor_secciones.update_one(
                {"_id": ObjectId(id)},
                {"$set": body}
            )
        except Exception as e:
            print("error", e)
            return jsonify({"status": "error"})
        return jsonify({"status": "ok"})
    
    async def add_seccion(id_user):
        print("add_seccion")
        body = request.get_json()
        name = body["name"]
        cols = body["cols"]
        position = 1
        #buscar en mongo cuantos documentos tiene la coleccion users_visor_secciones
        try:
            count = mongo.db.users_visor_secciones.count_documents({})
            position = count + 1
        except Exception as e:
            print("error", e)
            return jsonify({"status": "error"})
        #ahora actualizar en mongo.db.users_visor_secciones
        try:
            print("body2", body)
            result = mongo.db.users_visor_secciones.insert_one(
              {
                "name": name,
                "cols": cols,
                "position": position,
                "componentes": [], 
                "id_user": id_user
              }
            )
            inserted_id = str(result.inserted_id)
        except Exception as e:
            print("error", e)
            return jsonify({"status": "error"})
        return jsonify({"status": "ok", "id": inserted_id})
    
    async def delete_seccion(id):
        print("delete_seccion")
        try:
            mongo.db.users_visor_secciones.delete_one({"_id": ObjectId(id)})
        except Exception as e:
            print("error", e)
            return jsonify({"status": "error"})
        return jsonify({"status": "ok"})
        