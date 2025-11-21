from flask import Blueprint, jsonify, request
from app.db import get_connection

sala_routes = Blueprint('sala_routes', __name__)

@sala_routes.route("/salas", methods=["POST"])
def crear_sala():
    data = request.json
    nombre_sala = data.get("nombre_sala")
    id_edificio = data.get("id_edificio")
    capacidad = data.get("capacidad")
    tipo_sala = data.get("tipo_sala")

    if not all([nombre_sala, id_edificio, capacidad, tipo_sala]):
        return jsonify({"error": "Faltan datos obligatorios"}), 400

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM sala WHERE nombre_sala = %s AND id_edificio = %s",
                   (nombre_sala, id_edificio))
    existente = cursor.fetchone()
    if existente:
        conn.close()
        return jsonify({"error": "La sala ya existe"}), 409

    cursor.execute("""
        INSERT INTO sala (nombre_sala, id_edificio, capacidad, tipo_sala)
        VALUES (%s, %s, %s, %s)
    """, (nombre_sala, id_edificio, capacidad, tipo_sala))
    conn.commit()
    conn.close()
    return jsonify({"mensaje": "Sala creada correctamente"}), 201


@sala_routes.route("/salas", methods=["GET"])
def listar_salas():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM sala")
    salas = cursor.fetchall()
    conn.close()
    return jsonify(salas), 200


@sala_routes.route("/salas/<int:id_sala>", methods=["GET"])
def obtener_sala(id_sala):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM sala WHERE id_sala = %s", (id_sala,))
    sala = cursor.fetchone()
    conn.close()

    if sala:
        return jsonify(sala), 200
    return jsonify({"error": "Sala no encontrada"}), 404


@sala_routes.route("/salas/<int:id_sala>", methods=["PUT"])
def modificar_sala(id_sala):
    data = request.json
    nombre_sala = data.get("nombre_sala")
    id_edificio = data.get("id_edificio")
    capacidad = data.get("capacidad")
    tipo_sala = data.get("tipo_sala")

    if not all([nombre_sala, id_edificio, capacidad, tipo_sala]):
        return jsonify({"error": "Faltan datos obligatorios"}), 400

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM sala WHERE id_sala = %s", (id_sala,))
    existe = cursor.fetchone()
    if not existe:
        conn.close()
        return jsonify({"error": "Sala no encontrada"}), 404

    cursor.execute("""
        UPDATE sala
        SET nombre_sala = %s, id_edificio = %s, capacidad = %s, tipo_sala = %s
        WHERE id_sala = %s
    """, (nombre_sala, id_edificio, capacidad, tipo_sala, id_sala))
    conn.commit()
    conn.close()
    return jsonify({"mensaje": "Sala actualizada correctamente"}), 200


@sala_routes.route("/salas/<int:id_sala>", methods=["DELETE"])
def eliminar_sala(id_sala):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM sala WHERE id_sala = %s", (id_sala,))
    sala = cursor.fetchone()
    if not sala:
        conn.close()
        return jsonify({"error": "La sala no existe"}), 404

    cursor.execute("SELECT COUNT(*) AS total FROM reserva WHERE id_sala = %s", (id_sala,))
    reservas = cursor.fetchone()["total"]
    if reservas > 0:
        conn.close()
        return jsonify({"error": "No se puede eliminar la sala porque tiene reservas asociadas"}), 409

    cursor.execute("DELETE FROM sala WHERE id_sala = %s", (id_sala,))
    conn.commit()
    conn.close()
    return jsonify({"mensaje": "Sala eliminada correctamente"}), 200