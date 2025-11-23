from flask import Blueprint, request, jsonify
from app.db import get_connection
from datetime import datetime

reserva_routes = Blueprint('reserva_routes', __name__)


def convertir_timedelta(t):
    """Convierte timedelta → 'HH:MM:SS'"""
    if hasattr(t, "seconds"):
        segundos = t.seconds
        return f"{segundos//3600:02d}:{(segundos%3600)//60:02d}:00"
    return t

@reserva_routes.route("/reservas", methods=["GET"])
def obtener_reservas():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT r.id_reserva, r.fecha, r.estado,
               t.id_turno, t.hora_inicio, t.hora_fin,
               s.id_sala, s.nombre_sala,
               e.nombre_edificio
        FROM reserva r
        JOIN turno t ON t.id_turno = r.id_turno
        JOIN sala s ON s.id_sala = r.id_sala
        JOIN edificio e ON e.id_edificio = s.id_edificio
        ORDER BY r.fecha DESC, t.hora_inicio
    """)

    reservas = cursor.fetchall()
    conn.close()

    for r in reservas:
        r["hora_inicio"] = convertir_timedelta(r["hora_inicio"])
        r["hora_fin"] = convertir_timedelta(r["hora_fin"])

    return jsonify(reservas), 200

@reserva_routes.route("/reserva/<int:id_reserva>", methods=["GET"])
def obtener_reserva(id_reserva):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT r.*, s.nombre_sala, e.nombre_edificio
        FROM reserva r
        JOIN sala s ON s.id_sala = r.id_sala
        JOIN edificio e ON e.id_edificio = s.id_edificio
        WHERE r.id_reserva = %s
    """, (id_reserva,))

    reserva = cursor.fetchone()
    conn.close()

    if reserva:
        return jsonify(reserva), 200
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

    cursor.execute("SELECT tipo_sala, capacidad FROM sala WHERE id_sala = %s", (id_sala,))
    sala = cursor.fetchone()
    if not sala:
        conn.close()
        return jsonify({"error": "La sala no existe"}), 404

    tipo_sala = sala["tipo_sala"]
    capacidad_sala = sala["capacidad"]

    cursor.execute("SELECT * FROM turno WHERE id_turno = %s", (id_turno,))
    turno = cursor.fetchone()
    if not turno:
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
        return jsonify({"error": "La sala ya está reservada en ese turno"}), 400

    cursor.execute("""
        SELECT r.id_reserva
        FROM reserva r
        JOIN reserva_participante rp ON rp.id_reserva = r.id_reserva
        WHERE rp.ci_participante = %s AND r.fecha = %s AND r.id_turno = %s
              AND r.estado <> 'cancelada'
    """, (ci_participante, fecha, id_turno))
    if cursor.fetchone():
        conn.close()
        return jsonify({"error": "Ya tiene una reserva en ese turno"}), 400

    cursor.execute("""
        SELECT ppa.rol, pa.tipo
        FROM participante_programa_academico ppa
        JOIN programa_academico pa ON pa.id_programa = ppa.id_programa
        WHERE ppa.ci_participante = %s
    """, (ci_participante,))
    info = cursor.fetchone()

    es_estudiante_grado = info and info["rol"] == "alumno" and info["tipo"] == "grado"

    if es_estudiante_grado and tipo_sala != "libre":
        conn.close()
        return jsonify({"error": "Solo pueden reservar salas libres"}), 403

    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM reserva r
        JOIN reserva_participante rp ON rp.id_reserva = r.id_reserva
        WHERE rp.ci_participante = %s AND r.fecha = %s AND r.estado <> 'cancelada'
    """, (ci_participante, fecha))
    if cursor.fetchone()["total"] >= 2 and es_estudiante_grado:
        conn.close()
        return jsonify({"error": "Máximo 2 reservas por día"}), 400

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
    actualizado = cursor.rowcount
    conn.close()

    if actualizado == 0:
        return jsonify({"error": "La reserva no existe o ya está cancelada"}), 400

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
    actualizado = cursor.rowcount
    conn.close()

    if actualizado == 0:
        return jsonify({"error": "No se puede finalizar"}), 400

    return jsonify({"message": "Reserva finalizada"}), 200

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
    p = cursor.fetchone()
    if not p:
        conn.close()
        return jsonify({"error": "El participante no existe"}), 404

    cursor.execute("""
        SELECT * FROM reserva_participante
        WHERE id_reserva = %s AND ci_participante = %s
    """, (id_reserva, ci))
    if cursor.fetchone():
        conn.close()
        return jsonify({"error": "Ya está en esta reserva"}), 400

    cursor.execute("SELECT tipo_sala, capacidad FROM sala WHERE id_sala = %s", (id_sala,))
    sala = cursor.fetchone()
    tipo_sala = sala["tipo_sala"]
    capacidad = sala["capacidad"]

    cursor.execute("""
        SELECT ppa.rol, pa.tipo
        FROM participante_programa_academico ppa
        JOIN programa_academico pa ON pa.id_programa = ppa.id_programa
        WHERE ppa.ci_participante = %s
    """, (ci,))
    info = cursor.fetchone()

    es_estudiante_grado = info and info["rol"] == "alumno" and info["tipo"] == "grado"

    if es_estudiante_grado and tipo_sala != "libre":
        conn.close()
        return jsonify({"error": "Solo pueden agregarse a salas libres"}), 403

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
        WHERE rp.ci_participante = %s AND r.fecha = %s AND r.id_turno = %s
              AND r.estado <> 'cancelada'
    """, (ci, fecha, id_turno))
    if cursor.fetchone():
        conn.close()
        return jsonify({"error": "Ya tiene una reserva en ese turno"}), 400

    cursor.execute("""
        SELECT COUNT(*) AS ocupados
        FROM reserva_participante
        WHERE id_reserva = %s
    """, (id_reserva,))
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

@reserva_routes.route("/turnos", methods=["GET"])
def obtener_turnos():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM turno ORDER BY hora_inicio")
    turnos = cursor.fetchall()
    conn.close()

    for t in turnos:
        t["hora_inicio"] = convertir_timedelta(t["hora_inicio"])
        t["hora_fin"] = convertir_timedelta(t["hora_fin"])

    return jsonify(turnos), 200
