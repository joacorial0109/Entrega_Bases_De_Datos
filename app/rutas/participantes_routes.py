from flask import Blueprint, jsonify, request
from app.db import get_connection

participantes_routes = Blueprint('participantes_routes', __name__)

@participantes_routes.route("/participante", methods=["POST"])
def crear_participante():
    data = request.json
    ci = data.get("ci")
    nombre = data.get("nombre")
    apellido = data.get("apellido")
    email = data.get("email")
    id_login = data.get("id_login")

    if not all([ci, nombre, apellido, email]):
        return jsonify({"error": "Faltan datos obligatorios"}), 400

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO participante (ci, nombre, apellido, email, id_login)
        VALUES (%s, %s, %s, %s, %s)
    """, (ci, nombre, apellido, email, id_login))
    conn.commit()
    conn.close()
    return jsonify({"mensaje": "Participante creado"}), 201
