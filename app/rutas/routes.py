from flask import Blueprint, jsonify
from app.db import get_connection

routes = Blueprint('routes', __name__)

@routes.route("/salas")
def listar_salas():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM sala")
    salas = cursor.fetchall()
    conn.close()
    return jsonify(salas)
