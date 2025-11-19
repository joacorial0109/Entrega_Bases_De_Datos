from flask import Blueprint, jsonify, request
from app.db import get_connection

routes = Blueprint('routes', __name__)


# SALAS

@routes.route("/salas", methods=["GET"])
def listar_salas():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM sala")
    resultado = cursor.fetchall()
    conn.close()
    return jsonify(resultado)

# RESERVAS

@routes.route("/reserva", methods=["POST"])
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

@routes.route("/reservas", methods=["GET"])
def listar_reservas():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM reserva")
    resultado = cursor.fetchall()
    conn.close()
    return jsonify(resultado)

@routes.route("/reserva/<int:id_reserva>", methods=["GET"])
def obtener_reserva(id_reserva):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM reserva WHERE id_reserva = %s", (id_reserva,))
    fila = cursor.fetchone()
    conn.close()
    if fila:
        return jsonify(fila)
    return jsonify({"error": "Reserva no encontrada"}), 404

@routes.route("/reserva/<int:id_reserva>", methods=["PUT"])
def actualizar_reserva(id_reserva):
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
        SET id_sala = %s, fecha = %s, id_turno = %s
        WHERE id_reserva = %s
    """, (id_sala, fecha, id_turno, id_reserva))
    conn.commit()
    filas = cursor.rowcount
    conn.close()
    if filas:
        return jsonify({"mensaje": "Reserva actualizada"})
    return jsonify({"error": "Reserva no encontrada"}), 404

@routes.route("/reserva/<int:id_reserva>", methods=["DELETE"])
def eliminar_reserva(id_reserva):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM reserva WHERE id_reserva = %s", (id_reserva,))
    conn.commit()
    filas = cursor.rowcount
    conn.close()
    if filas:
        return jsonify({"mensaje": "Reserva eliminada"})
    return jsonify({"error": "Reserva no encontrada"}), 404


# PARTICIPANTES

@routes.route("/participante", methods=["POST"])
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

@routes.route("/participantes", methods=["GET"])
def listar_participantes():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM participante")
    resultado = cursor.fetchall()
    conn.close()
    return jsonify(resultado)

@routes.route("/participante/<string:ci>", methods=["GET"])
def obtener_participante(ci):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM participante WHERE ci = %s", (ci,))
    resultado = cursor.fetchone()
    conn.close()
    if resultado:
        return jsonify(resultado)
    return jsonify({"error": "Participante no encontrado"}), 404

@routes.route("/participante/<string:ci>", methods=["PUT"])
def actualizar_participante(ci):
    data = request.json
    nombre = data.get("nombre")
    apellido = data.get("apellido")
    email = data.get("email")
    id_login = data.get("id_login")

    if not all([nombre, apellido, email]):
        return jsonify({"error": "Faltan datos obligatorios"}), 400

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE participante
        SET nombre = %s, apellido = %s, email = %s, id_login = %s
        WHERE ci = %s
    """, (nombre, apellido, email, id_login, ci))
    conn.commit()
    filas = cursor.rowcount
    conn.close()
    if filas:
        return jsonify({"mensaje": "Participante actualizado"})
    return jsonify({"error": "Participante no encontrado"}), 404

@routes.route("/participante/<string:ci>", methods=["DELETE"])
def eliminar_participante(ci):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM participante WHERE ci = %s", (ci,))
    conn.commit()
    filas = cursor.rowcount
    conn.close()
    if filas:
        return jsonify({"mensaje": "Participante eliminado"})
    return jsonify({"error": "Participante no encontrado"}), 404
