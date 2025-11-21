from flask import Blueprint, jsonify
from app.db import get_connection

sala_routes = Blueprint('sala_routes', __name__)

@sala_routes.route("/salas", methods=["GET"])
def listar_salas():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM sala")
    resultado = cursor.fetchall()
    conn.close()
    return jsonify(resultado)
