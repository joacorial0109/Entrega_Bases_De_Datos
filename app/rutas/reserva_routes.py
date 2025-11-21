from flask import Blueprint, jsonify, request
from app.db import get_connection

reserva_routes = Blueprint('reserva_routes', __name__)

@reserva_routes.route("/reserva", methods=["POST"])
def crear_reserva():
    data = request.json
    id_sala = data.get("id_sala")
    fecha = data.get("fecha")
    id_turno = data.get("id_turno")
    estado = data.get("estado", "activa")

    if not all([id_sala, fecha, id_turno]):
        return jsonify({"error": "Faltan datos obligatorios"}), 400

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO reserva (id_sala, fecha, id_turno, estado)
        VALUES (%s, %s, %s, %s)
    """, (id_sala, fecha, id_turno, estado))
    conn.commit()
    conn.close()
    return jsonify({"mensaje": "Reserva creada"}), 201


@reserva_routes.route("/reservas", methods=["GET"])
def obtener_reservas():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM reserva")
    reservas = cursor.fetchall()
    conn.close()
    return jsonify(reservas), 200


@reserva_routes.route("/reserva/<int:id_reserva>", methods=["PUT"])
def modificar_reserva(id_reserva):
    data = request.json
    id_sala = data.get("id_sala")
    fecha = data.get("fecha")
    id_turno = data.get("id_turno")

    if not all([id_sala, fecha, id_turno]):
        return jsonify({"error": "Faltan datos obligatorios"}), 400

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE reserva
        SET id_sala=%s, fecha=%s, id_turno=%s
        WHERE id_reserva=%s
    """, (id_sala, fecha, id_turno, id_reserva))
    conn.commit()
    filas = cursor.rowcount
    conn.close()

    if filas == 0:
        return jsonify({"error": "Reserva no encontrada"}), 404

    return jsonify({"mensaje": "Reserva actualizada"}), 200


@reserva_routes.route("/reserva/<int:id_reserva>", methods=["DELETE"])
def cancelar_reserva(id_reserva):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE reserva
        SET estado='cancelada'
        WHERE id_reserva=%s
    """, (id_reserva,))
    conn.commit()
    filas = cursor.rowcount
    conn.close()

    if filas == 0:
        return jsonify({"error": "Reserva no encontrada"}), 404

    return jsonify({"mensaje": "Reserva cancelada"}), 200


@reserva_routes.route("/reserva/<int:id_reserva>/participante", methods=["POST"])
def agregar_participante_reserva(id_reserva):
    data = request.json
    ci = data.get("ci")

    if not ci:
        return jsonify({"error": "Debe especificar un CI"}), 400

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO reserva_participante (id_reserva, ci_participante)
        VALUES (%s, %s)
    """, (id_reserva, ci))
    conn.commit()
    conn.close()

    return jsonify({"mensaje": "Participante agregado a la reserva"}), 201


@reserva_routes.route("/reserva/<int:id_reserva>/asistencia", methods=["PUT"])
def registrar_asistencia(id_reserva):
    data = request.json
    ci = data.get("ci")
    asistencia = data.get("asistencia")

    if ci is None or asistencia is None:
        return jsonify({"error": "Debe especificar CI y asistencia"}), 400

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE reserva_participante
        SET asistencia=%s
        WHERE id_reserva=%s AND ci_participante=%s
    """, (asistencia, id_reserva, ci))
    conn.commit()
    filas = cursor.rowcount
    conn.close()

    if filas == 0:
        return jsonify({"error": "No existe el participante en la reserva"}), 404

    return jsonify({"mensaje": "Asistencia actualizada"}), 200