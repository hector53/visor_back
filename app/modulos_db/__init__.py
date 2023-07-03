import pymysql
from app.modulos_db.poolmysql import ConnectionPool
from app.datos_db import *
db_config = {
    'host': host,
    'user': userDb,
    'password': userPass,
    'database': database,
    'autocommit': True
}
pool = ConnectionPool(**db_config, maxsize=6)
import logging

log = logging.getLogger(__name__)

def register_user(sql, params):
    con = pool.get_connection()
    try:
        with con.cursor() as cur:
            cur.execute(sql, params )
            return {"status": 1, "id": cur.lastrowid}
    except pymysql.Error as e:
        log.warning(f"errrorr: {e}")
        return {"status": 0, "error": e.args[1]}
    finally:
        con.close()

def insert_data(sql, params):
    con = pool.get_connection()
    try:
        with con.cursor() as cur:
            cur.execute(sql, params )
            return {"status": 1, "id": cur.lastrowid}
    except pymysql.Error as e:
        print("errrorr", e)
        return {"status": 0, "error": e.args[1]}
    finally:
        con.close()

def verificar_email(email, sql):
    con = pool.get_connection()
    try:
        with con.cursor() as cur:
            cur.execute(sql, (email) )
            rows = cur.fetchone()
            return rows
    finally:
        con.close()

def getDataOnly(consulta):
    con = pool.get_connection()
    try:
        with con.cursor() as cur:
            cur.execute(consulta)
            rows = cur.fetchall()
            return rows
    except pymysql.Error as e:
        log.warning(f"errrorr: {e}")
        return {"status": 0, "error": e.args[1]}
    finally:
        con.close()


def getData(consulta, params):
    con = pool.get_connection()
    try:
        with con.cursor() as cur:
            cur.execute(consulta, params)
            rows = cur.fetchall()
            return rows
    except pymysql.Error as e:
        log.warning(f"errrorr: {e}")
        return {"status": 0, "error": e.args[1]}
    finally:
        con.close()
def getDataOne(consulta, params):
    con = pool.get_connection()
    try:
        with con.cursor() as cur:
            cur.execute(consulta, params)
            rows = cur.fetchone()
            return rows
    finally:
        con.close()
def updateData(consulta, params):
    con = pool.get_connection()
    try:
        with con.cursor() as cur:
            guardar = cur.execute(consulta, params)
            return cur.lastrowid
    except pymysql.Error as e:
        print("errrorr", e)
        return 0
    finally:
        con.close()

def updateTable(consulta, params):
    con = pool.get_connection()
    try:
        with con.cursor() as cur:
            guardar = cur.execute(consulta, params)
            return 1
    except pymysql.Error as e:
        print("errrorr", e)
        return 0
    finally:
        con.close()