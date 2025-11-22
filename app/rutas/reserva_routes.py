from flask import Blueprint, request, jsonify
from app.db import get_connection
from datetime import datetime, timedelta

reserva_routes = Blueprint('reserva_routes', __name__)

@reserva_routes.route("/reservas", methods=["GET"])
def obtener_reservas():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM reserva")
    reservas = cursor.fetchall()
    conn.close()
    return jsonify(reservas), 200

@reserva_routes.route("/reserva/<int:id_reserva>", methods=["GET"])
def obtener_reserva(id_reserva):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM reserva WHERE id_reserva = %s", (id_reserva,))
    reserva = cursor.fetchone()
    conn.close()

    if reserva:
        return jsonify(reserva), 200
    else:
        return jsonify({"error": "Reserva no encontrada"}), 404

@reserva_routes.route("/reserva/<int:id_reserva>/participantes", methods=["GET"])
def participantes_de_reserva(id_reserva):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT rp.ci_participante, p.nombre, p.apellido, rp.asistencia
        FROM reserva_participante rp
        JOIN participante p ON p.ci = rp.ci_participante
        WHERE rp.id_reserva = %s
    """, (id_reserva,))
    participantes = cursor.fetchall()
    conn.close()
    return jsonify(participantes), 200

@reserva_routes.route("/reservas", methods=["POST"])
def crear_reserva():
    data = request.get_json()
    id_sala = data.get("id_sala")
    fecha = data.get("fecha")
    id_turno = data.get("id_turno")
    ci_participante = data.get("ci_participante")

    if not all([id_sala, fecha, id_turno, ci_participante]):
        return jsonify({"error": "Faltan datos obligatorios"}), 400

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT ci FROM participante WHERE ci = %s", (ci_participante,))
    if not cursor.fetchone():
        conn.close()
        return jsonify({"error": "El participante no existe"}), 404

    cursor.execute("SELECT tipo_sala FROM sala WHERE id_sala = %s", (id_sala,))
    sala_info = cursor.fetchone()
    if not sala_info:
        conn.close()
        return jsonify({"error": "La sala no existe"}), 404
    tipo_sala = sala_info["tipo_sala"]

    cursor.execute("SELECT id_turno FROM turno WHERE id_turno = %s", (id_turno,))
    if not cursor.fetchone():
        conn.close()
        return jsonify({"error": "El turno no existe"}), 404

    cursor.execute("""
        SELECT id_sancion FROM sancion_participante
        WHERE ci_participante = %s AND fecha_inicio <= %s AND fecha_fin >= %s
    """, (ci_participante, fecha, fecha))
    if cursor.fetchone():
        conn.close()
        return jsonify({"error": "El participante está sancionado"}), 400
    cursor.execute("""
        SELECT id_reserva FROM reserva
        WHERE id_sala = %s AND fecha = %s AND id_turno = %s AND estado <> 'cancelada'
    """, (id_sala, fecha, id_turno))
    if cursor.fetchone():
        conn.close()
        return jsonify({"error": "Sala ya reservada en ese turno"}), 400

    cursor.execute("""
        SELECT r.id_reserva FROM reserva r
        JOIN reserva_participante rp ON rp.id_reserva = r.id_reserva
        WHERE r.fecha = %s AND r.id_turno = %s AND rp.ci_participante = %s AND r.estado <> 'cancelada'
    """, (fecha, id_turno, ci_participante))
    if cursor.fetchone():
        conn.close()
        return jsonify({"error": "Ya tiene reserva en ese turno"}), 400

    cursor.execute("""
        SELECT ppa.rol, pa.tipo FROM participante_programa_academico ppa
        JOIN programa_academico pa ON pa.id_programa = ppa.id_programa
        WHERE ppa.ci_participante = %s
    """, (ci_participante,))
    datos = cursor.fetchone()

    if datos is None:
        es_estudiante_grado = True
    else:
        es_estudiante_grado = datos["rol"] == "alumno" and datos["tipo"] == "grado"

    if es_estudiante_grado and tipo_sala != "libre":
        conn.close()
        return jsonify({"error": "Estudiantes de grado solo pueden reservar salas de uso libre"}), 403

    if es_estudiante_grado:
        cursor.execute("""
            SELECT COUNT(*) AS total FROM reserva r
            JOIN reserva_participante rp ON rp.id_reserva = r.id_reserva
            WHERE rp.ci_participante = %s AND r.fecha = %s AND r.estado <> 'cancelada'
        """, (ci_participante, fecha))
        if cursor.fetchone()["total"] >= 2:
            conn.close()
            return jsonify({"error": "Máximo de 2 reservas por día"}), 400

        cursor.execute("""
            SELECT COUNT(*) AS total FROM reserva r
            JOIN reserva_participante rp ON rp.id_reserva = r.id_reserva
            WHERE rp.ci_participante = %s AND YEARWEEK(r.fecha, 1) = YEARWEEK(%s, 1) AND r.estado <> 'cancelada'
        """, (ci_participante, fecha))
        if cursor.fetchone()["total"] >= 3:
            conn.close()
            return jsonify({"error": "Máximo de 3 reservas por semana"}), 400

    cursor.execute("""
        INSERT INTO reserva (id_sala, fecha, id_turno, estado)
        VALUES (%s, %s, %s, 'activa')
    """, (id_sala, fecha, id_turno))
    id_reserva = cursor.lastrowid

    cursor.execute("""
        INSERT INTO reserva_participante (id_reserva, ci_participante, asistencia)
        VALUES (%s, %s, %s)
    """, (id_reserva, ci_participante, False))

    conn.commit()
    conn.close()

    return jsonify({"message": "Reserva creada", "id_reserva": id_reserva}), 201


@reserva_routes.route("/reserva/<int:id_reserva>/cancelar", methods=["PUT"])
def cancelar_reserva(id_reserva):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE reserva
        SET estado = 'cancelada'
        WHERE id_reserva = %s AND estado = 'activa'
    """, (id_reserva,))
    conn.commit()
    filas = cursor.rowcount
    conn.close()

    if filas == 0:
        return jsonify({"error": "La reserva no existe o no está en estado 'activa'"}), 400

    return jsonify({"message": "Reserva cancelada"}), 200


@reserva_routes.route("/reserva/<int:id_reserva>/finalizar", methods=["PUT"])
def finalizar_reserva(id_reserva):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE reserva
        SET estado = 'finalizada'
        WHERE id_reserva = %s AND estado = 'activa'
    """, (id_reserva,))
    conn.commit()
    filas = cursor.rowcount
    conn.close()

    if filas == 0:
        return jsonify({"error": "La reserva no existe o no está en estado 'activa'"}), 400

    return jsonify({"message": "Reserva finalizada"}), 200

@reserva_routes.route("/reserva/<int:id_reserva>/asistencia", methods=["PUT"])
def registrar_asistencia(id_reserva):
    data = request.get_json()
    ci = data.get("ci")
    asistencia = data.get("asistencia")

    if ci is None or asistencia is None:
        return jsonify({"error": "Debe indicar ci y asistencia"}), 400

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE reserva_participante
        SET asistencia = %s
        WHERE id_reserva = %s AND ci_participante = %s
    """, (asistencia, id_reserva, ci))
    conn.commit()
    filas = cursor.rowcount
    conn.close()

    if filas == 0:
        return jsonify({"error": "No existe el participante en la reserva indicada"}), 404

    return jsonify({"message": "Asistencia actualizada"}), 200


@reserva_routes.route("/reserva/<int:id_reserva>/participantes", methods=["POST"])
def agregar_participante_reserva(id_reserva):
    data = request.get_json()
    ci = data.get("ci_participante")

    if not ci:
        return jsonify({"error": "Debe indicar ci_participante"}), 400

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM reserva WHERE id_reserva = %s AND estado <> 'cancelada'", (id_reserva,))
    reserva = cursor.fetchone()
    if not reserva:
        conn.close()
        return jsonify({"error": "La reserva no existe"}), 404

    fecha = reserva["fecha"]
    id_turno = reserva["id_turno"]
    id_sala = reserva["id_sala"]

    cursor.execute("SELECT * FROM participante WHERE ci = %s", (ci,))
    participante = cursor.fetchone()
    if not participante:
        conn.close()
        return jsonify({"error": "El participante no existe"}), 404

    cursor.execute("SELECT * FROM reserva_participante WHERE id_reserva = %s AND ci_participante = %s", (id_reserva, ci))
    if cursor.fetchone():
        conn.close()
        return jsonify({"error": "El participante ya está en esta reserva"}), 400

    # Obtener tipo de sala
    cursor.execute("SELECT tipo_sala FROM sala WHERE id_sala = %s", (id_sala,))
    tipo_sala = cursor.fetchone()["tipo_sala"]

    # Verificar tipo y rol del participante
    cursor.execute("""
        SELECT ppa.rol, pa.tipo
        FROM participante_programa_academico ppa
        JOIN programa_academico pa ON pa.id_programa = ppa.id_programa
        WHERE ppa.ci_participante = %s
    """, (ci,))
    datos = cursor.fetchone()

    if datos is None:
        es_estudiante_grado = True
    else:
        es_estudiante_grado = datos["rol"] == "alumno" and datos["tipo"] == "grado"

    if es_estudiante_grado and tipo_sala != "libre":
        conn.close()
        return jsonify({"error": "Estudiantes de grado solo pueden agregarse a salas de uso libre"}), 403

    cursor.execute("""
        SELECT * FROM sancion_participante
        WHERE ci_participante = %s AND fecha_inicio <= %s AND fecha_fin >= %s
    """, (ci, fecha, fecha))
    if cursor.fetchone():
        conn.close()
        return jsonify({"error": "El participante está sancionado"}), 400

    cursor.execute("""
        SELECT r.id_reserva
        FROM reserva r
        JOIN reserva_participante rp ON rp.id_reserva = r.id_reserva
        WHERE rp.ci_participante = %s AND r.fecha = %s AND r.id_turno = %s AND r.estado <> 'cancelada'
    """, (ci, fecha, id_turno))
    if cursor.fetchone():
        conn.close()
        return jsonify({"error": "Ya tiene una reserva en ese turno"}), 400

    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM reserva r
        JOIN reserva_participante rp ON rp.id_reserva = r.id_reserva
        WHERE rp.ci_participante = %s AND r.fecha = %s AND r.estado <> 'cancelada'
    """, (ci, fecha))
    if cursor.fetchone()["total"] >= 2 and es_estudiante_grado:
        conn.close()
        return jsonify({"error": "Máximo de 2 reservas por día"}), 400

    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM reserva r
        JOIN reserva_participante rp ON rp.id_reserva = r.id_reserva
        WHERE rp.ci_participante = %s AND YEARWEEK(r.fecha, 1) = YEARWEEK(%s, 1) AND r.estado <> 'cancelada'
    """, (ci, fecha))
    if cursor.fetchone()["total"] >= 3 and es_estudiante_grado:
        conn.close()
        return jsonify({"error": "Máximo de 3 reservas por semana"}), 400

    cursor.execute("SELECT capacidad FROM sala WHERE id_sala = %s", (id_sala,))
    capacidad = cursor.fetchone()["capacidad"]

    cursor.execute("SELECT COUNT(*) AS ocupados FROM reserva_participante WHERE id_reserva = %s", (id_reserva,))
    if cursor.fetchone()["ocupados"] >= capacidad:
        conn.close()
        return jsonify({"error": "La sala está llena"}), 400

    cursor.execute("""
        INSERT INTO reserva_participante (id_reserva, ci_participante, asistencia)
        VALUES (%s, %s, %s)
    """, (id_reserva, ci, False))

    conn.commit()
    conn.close()

    return jsonify({"message": "Participante agregado correctamente"}), 201
