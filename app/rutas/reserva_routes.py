from flask import Blueprint, jsonify, request
from app.db import get_connection

reserva_routes = Blueprint('reserva_routes', _name_)

@reserva_routes.route("/reserva", methods=["POST"])
def crear_reserva():
    data = request.json
    id_sala = data.get("id_sala")
    fecha = data.get("fecha")
    id_turno = data.get("id_turno")
    ci_participante = data.get("ci_participante")

    if not all([id_sala, fecha, id_turno, ci_participante]):
        return jsonify({"error": "Faltan datos obligatorios"}), 400

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT COUNT(*) AS cant
        FROM sancion_participante
        WHERE ci_participante=%s
        AND %s BETWEEN fecha_inicio AND fecha_fin
    """, (ci_participante, fecha))
    if cursor.fetchone()["cant"] > 0:
        conn.close()
        return jsonify({"error": "El participante está sancionado y no puede reservar"}), 403

    cursor.execute("""
        SELECT COUNT(*) AS cant
        FROM reserva_participante rp
        JOIN reserva r ON r.id_reserva = rp.id_reserva
        WHERE rp.ci_participante=%s AND r.fecha=%s
    """, (ci_participante, fecha))
    if cursor.fetchone()["cant"] >= 2:
        conn.close()
        return jsonify({"error": "No puede reservar más de 2 horas en el mismo día"}), 403

    cursor.execute("""
        SELECT COUNT(*) AS cant
        FROM reserva_participante rp
        JOIN reserva r ON r.id_reserva = rp.id_reserva
        WHERE rp.ci_participante=%s
        AND r.estado='activa'
        AND YEARWEEK(r.fecha) = YEARWEEK(%s)
    """, (ci_participante, fecha))
    if cursor.fetchone()["cant"] >= 3:
        conn.close()
        return jsonify({"error": "Límite semanal: no puede tener más de 3 reservas activas"}), 403

    cursor.execute("""
        SELECT COUNT(*) AS cant
        FROM reserva
        WHERE id_sala=%s AND fecha=%s AND id_turno=%s AND estado='activa'
    """, (id_sala, fecha, id_turno))
    if cursor.fetchone()["cant"] > 0:
        conn.close()
        return jsonify({"error": "La sala ya está reservada en ese turno"}), 403

    cursor.execute("""
        SELECT COUNT(*) AS cant
        FROM reserva r
        JOIN reserva_participante rp ON rp.id_reserva=r.id_reserva
        WHERE rp.ci_participante=%s AND r.fecha=%s AND r.id_turno=%s AND r.estado='activa'
    """, (ci_participante, fecha, id_turno))
    if cursor.fetchone()["cant"] > 0:
        conn.close()
        return jsonify({"error": "Ya tiene una reserva en ese turno"}, 403)

    cursor.execute("""
        INSERT INTO reserva (id_sala, fecha, id_turno, estado)
        VALUES (%s, %s, %s, 'activa')
    """, (id_sala, fecha, id_turno))
    id_reserva = cursor.lastrowid

    cursor.execute("""
        INSERT INTO reserva_participante (id_reserva, ci_participante)
        VALUES (%s, %s)
    """, (id_reserva, ci_participante))

    conn.commit()
    conn.close()

    return jsonify({"mensaje": "Reserva creada", "id_reserva": id_reserva}), 201


@reserva_routes.route("/reservas", methods=["GET"])
def listar_reservas():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM reserva")
    reservas = cursor.fetchall()
    conn.close()
    return jsonify(reservas), 200


@reserva_routes.route("/reserva/<int:id_reserva>/participante", methods=["POST"])
def agregar_participante(id_reserva):
    data = request.json
    ci = data.get("ci")

    conn = get_connection()
    cursor = conn.cursor()

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
    ci = data.get("ci")
    asistencia = data.get("asistencia")

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


@reserva_routes.route("/reserva/<int:id_reserva>", methods=["DELETE"])
def cancelar_reserva(id_reserva):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("UPDATE reserva SET estado='cancelada' WHERE id_reserva=%s", (id_reserva,))
    conn.commit()
    conn.close()

    return jsonify({"mensaje": "Reserva cancelada"}), 200


@reserva_routes.route("/reserva/<int:id_reserva>/finalizar", methods=["PUT"])
def finalizar_reserva(id_reserva):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT COUNT(*) AS cant
        FROM reserva_participante
        WHERE id_reserva=%s AND asistencia=TRUE
    """, (id_reserva,))
    asistentes = cursor.fetchone()["cant"]

    if asistentes == 0:
        cursor.execute("""
            UPDATE reserva SET estado='sin_asistencia'
            WHERE id_reserva=%s
        """, (id_reserva,))
    else:
        cursor.execute("""
            UPDATE reserva SET estado='finalizada'
            WHERE id_reserva=%s
        """, (id_reserva,))

    conn.commit()
    conn.close()

    return jsonify({"mensaje": "Reserva finalizada"}), 200


@reserva_routes.route("/disponibilidad", methods=["GET"])
def disponibilidad():
    id_sala = request.args.get("id_sala")
    fecha = request.args.get("fecha")
    id_turno = request.args.get("id_turno")

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT COUNT(*) AS cant
        FROM reserva
        WHERE id_sala=%s AND fecha=%s AND id_turno=%s AND estado='activa'
    """, (id_sala, fecha, id_turno))

    disponible = cursor.fetchone()["cant"] == 0
    conn.close()

    return jsonify({"disponible": disponible}), 200