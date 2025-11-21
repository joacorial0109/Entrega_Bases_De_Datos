from flask import Blueprint, jsonify, request
from app.db import get_connection

sala_routes = Blueprint('sala_routes')

@sala_routes.route("/salas", methods=["GET"])
def obtener_salas():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM sala")
    salas = cursor.fetchall()
    conn.close()
    return jsonify(salas), 200


@sala_routes.route("/sala", methods=["POST"])
def crear_sala():
    data = request.json
    nombre_sala = data.get("nombre_sala")
    id_edificio = data.get("id_edificio")
    capacidad = data.get("capacidad")
    tipo_sala = data.get("tipo_sala")

    if not all([nombre_sala, id_edificio, capacidad, tipo_sala]):
        return jsonify({"error": "Faltan datos obligatorios"}), 400

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO sala (nombre_sala, id_edificio, capacidad, tipo_sala)
        VALUES (%s, %s, %s, %s)
    """, (nombre_sala, id_edificio, capacidad, tipo_sala))
    conn.commit()
    conn.close()
    return jsonify({"mensaje": "Sala creada"}), 201


@sala_routes.route("/sala/<int:id_sala>", methods=["PUT"])
def modificar_sala(id_sala):
    data = request.json
    nombre_sala = data.get("nombre_sala")
    id_edificio = data.get("id_edificio")
    capacidad = data.get("capacidad")
    tipo_sala = data.get("tipo_sala")

    if not all([nombre_sala, id_edificio, capacidad, tipo_sala]):
        return jsonify({"error": "Faltan datos obligatorios"}), 400

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE sala
        SET nombre_sala=%s, id_edificio=%s, capacidad=%s, tipo_sala=%s
        WHERE id_sala=%s
    """, (nombre_sala, id_edificio, capacidad, tipo_sala, id_sala))
    conn.commit()
    filas = cursor.rowcount
    conn.close()

    if filas == 0:
        return jsonify({"error": "Sala no encontrada"}), 404

    return jsonify({"mensaje": "Sala actualizada"}), 200


@sala_routes.route("/sala/<int:id_sala>", methods=["DELETE"])
def eliminar_sala(id_sala):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM sala WHERE id_sala=%s", (id_sala,))
    conn.commit()
    filas = cursor.rowcount
    conn.close()

    if filas == 0:
        return jsonify({"error": "Sala no encontrada"}), 404

    return jsonify({"mensaje": "Sala eliminada"}), 200