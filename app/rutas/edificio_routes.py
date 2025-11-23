from flask import Blueprint, jsonify
from app.db import get_connection

edificio_routes = Blueprint('edificio_routes', __name__)

@edificio_routes.route("/edificios", methods=["GET"])
def listar_edificios():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT id_edificio, nombre_edificio
        FROM edificio
        ORDER BY id_edificio
    """)

    edificios = cursor.fetchall()
    conn.close()
    return jsonify(edificios), 200
