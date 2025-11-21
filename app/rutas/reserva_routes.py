from flask import Blueprint, request, jsonify
from app.db import get_connection
from datetime import datetime, timedelta

reserva_routes = Blueprint('reserva_routes')


@reserva_routes.route("/reservas", methods=["GET"])
def listar_reservas():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT r.id_reserva, r.fecha, r.id_turno, r.estado, s.nombre_sala
        FROM reserva r
        JOIN sala s ON s.id_sala = r.id_sala
        ORDER BY r.fecha, r.id_turno
    """)
    data = cursor.fetchall()
    conn.close()
    return jsonify(data), 200


@reserva_routes.route("/reservas", methods=["POST"])
def crear_reserva():
    data = request.json
    id_sala = data["id_sala"]
    fecha = data["fecha"]
    id_turno = data["id_turno"]
    ci_participante = data["ci_participante"]

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT * FROM sancion_participante
        WHERE ci_participante=%s
        AND fecha_inicio <= %s
        AND fecha_fin >= %s
    """, (ci_participante, fecha, fecha))
    sancion = cursor.fetchone()
    if sancion:
        conn.close()
        return jsonify({"error": "El participante está sancionado"}), 400

    cursor.execute("""
        SELECT COUNT(*) AS total FROM reserva r
        JOIN reserva_participante rp ON rp.id_reserva = r.id_reserva
        WHERE rp.ci_participante=%s AND r.fecha=%s
    """, (ci_participante, fecha))
    if cursor.fetchone()["total"] >= 2:
        conn.close()
        return jsonify({"error": "Máximo 2 reservas por día"}), 400

    semana_inicio = (datetime.strptime(fecha, "%Y-%m-%d") - timedelta(days=7)).strftime("%Y-%m-%d")
    cursor.execute("""
        SELECT COUNT(*) AS total FROM reserva r
        JOIN reserva_participante rp ON rp.id_reserva = r.id_reserva
        WHERE rp.ci_participante=%s
        AND r.fecha BETWEEN %s AND %s
    """, (ci_participante, semana_inicio, fecha))
    if cursor.fetchone()["total"] >= 3:
        conn.close()
        return jsonify({"error": "Máximo 3 reservas activas por semana"}), 400

    cursor.execute("""
        SELECT * FROM reserva
        WHERE id_sala=%s AND fecha=%s AND id_turno=%s
    """, (id_sala, fecha, id_turno))
    if cursor.fetchone():
        conn.close()
        return jsonify({"error": "La sala ya está reservada en ese turno"}), 400

    cursor.execute("""
        SELECT * FROM reserva r
        JOIN reserva_participante rp ON rp.id_reserva = r.id_reserva
        WHERE rp.ci_participante=%s AND r.fecha=%s AND r.id_turno=%s
    """, (ci_participante, fecha, id_turno))
    if cursor.fetchone():
        conn.close()
        return jsonify({"error": "El participante ya tiene reserva en ese turno"}), 400

    cursor.execute("""
        INSERT INTO reserva (id_sala, fecha, id_turno, estado)
        VALUES (%s, %s, %s, 'activa')
    """, (id_sala, fecha, id_turno))
    conn.commit()

    id_reserva = cursor.lastrowid

    cursor.execute("""
        INSERT INTO reserva_participante (id_reserva, ci_participante, asistencia)
        VALUES (%s, %s, FALSE)
    """, (id_reserva, ci_participante))
    conn.commit()

    conn.close()
    return jsonify({"mensaje": "Reserva creada", "id_reserva": id_reserva}), 201


@reserva_routes.route("/reserva/<int:id_reserva>/participantes", methods=["POST"])
def agregar_participante_reserva(id_reserva):
    data = request.json
    ci = data["ci"]

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        INSERT INTO reserva_participante (id_reserva, ci_participante)
        VALUES (%s, %s)
    """, (id_reserva, ci))
    conn.commit()
    conn.close()

    return jsonify({"mensaje": "Participante agregado"}), 201


@reserva_routes.route("/reserva/<int:id_reserva>/asistencia", methods=["PUT"])
def registrar_asistencia(id_reserva):
    data = request.json
    ci = data["ci"]
    asistencia = data["asistencia"]

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE reserva_participante
        SET asistencia=%s
        WHERE id_reserva=%s AND ci_participante=%s
    """, (asistencia, id_reserva, ci))
    conn.commit()
    conn.close()

    return jsonify({"mensaje": "Asistencia actualizada"}), 200


@reserva_routes.route("/reserva/<int:id_reserva>/cancelar", methods=["PUT"])
def cancelar_reserva(id_reserva):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE reserva
        SET estado='cancelada'
        WHERE id_reserva=%s
    """, (id_reserva,))
    conn.commit()
    conn.close()

    return jsonify({"mensaje": "Reserva cancelada"}), 200


@reserva_routes.route("/reserva/<int:id_reserva>/finalizar", methods=["PUT"])
def finalizar_reserva(id_reserva):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT asistencia FROM reserva_participante
        WHERE id_reserva=%s
    """, (id_reserva,))
    asistencias = cursor.fetchall()

    if not asistencias:
        conn.close()
        return jsonify({"error": "La reserva no tiene participantes"}), 400

    todos_asistieron = all([a["asistencia"] for a in asistencias])

    nuevo_estado = "finalizada" if todos_asistieron else "sin_asistencia"

    cursor.execute("""
        UPDATE reserva
        SET estado=%s
        WHERE id_reserva=%s
    """, (nuevo_estado, id_reserva))
    conn.commit()
    conn.close()

    return jsonify({"mensaje": "Reserva finalizada", "estado": nuevo_estado}), 200


@reserva_routes.route("/disponibilidad", methods=["GET"])
def disponibilidad():
    id_sala = request.args.get("id_sala")
    fecha = request.args.get("fecha")

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM turno")
    turnos = cursor.fetchall()

    cursor.execute("""
        SELECT id_turno FROM reserva
        WHERE id_sala=%s AND fecha=%s
    """, (id_sala, fecha))
    ocupados = {row["id_turno"] for row in cursor.fetchall()}

    disponibles = [t for t in turnos if t["id_turno"] not in ocupados]

    conn.close()
    return jsonify(disponibles), 200


@reserva_routes.route("/reserva/<int:id_reserva>", methods=["GET"])
def obtener_reserva(id_reserva):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT r.id_reserva, r.fecha, r.id_turno, r.estado, s.id_sala, s.nombre_sala
        FROM reserva r
        JOIN sala s ON s.id_sala = r.id_sala
        WHERE r.id_reserva=%s
    """, (id_reserva,))
    reserva = cursor.fetchone()
    conn.close()

    if not reserva:
        return jsonify({"error": "Reserva no encontrada"}), 404

    return jsonify(reserva), 200


@reserva_routes.route("/reserva/<int:id_reserva>/participantes", methods=["GET"])
def obtener_participantes_reserva(id_reserva):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT rp.ci_participante, p.nombre, p.apellido, rp.asistencia
        FROM reserva_participante rp
        JOIN participante p ON p.ci = rp.ci_participante
        WHERE rp.id_reserva=%s
    """, (id_reserva,))
    participantes = cursor.fetchall()
    conn.close()

    return jsonify(participantes), 200