from flask import Blueprint, jsonify, request
from app.db import get_connection

reserva_routes = Blueprint('reserva_routes', __name__)

@reserva_routes.route("/reserva", methods=["POST"])
def crear_reserva():
    data = request.json
    id_sala = data.get("id_sala")
    fecha = data.get("fecha")
    id_turno = data.get("id_turno")

    if not all([id_sala, fecha, id_turno]):
        return jsonify({"error": "Faltan datos obligatorios"}), 400

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO reserva (id_sala, fecha, id_turno)
        VALUES (%s, %s, %s)
    """, (id_sala, fecha, id_turno))
    conn.commit()
    id_generado = cursor.lastrowid
    conn.close()

    return jsonify({"mensaje": "Reserva creada", "id_reserva": id_generado}), 201

@reserva_routes.route("/reservas", methods=["GET"])
def listar_reservas():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM reserva")
    resultado = cursor.fetchall()
    conn.close()
    return jsonify(resultado)
