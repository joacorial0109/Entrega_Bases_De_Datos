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


@participantes_routes.route("/participantes", methods=["GET"])
def listar_participantes():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM participante")
    participantes = cursor.fetchall()
    conn.close()
    return jsonify(participantes), 200


@participantes_routes.route("/participante/<ci>", methods=["GET"])
def obtener_participante(ci):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM participante WHERE ci = %s", (ci,))
    participante = cursor.fetchone()
    conn.close()

    if participante:
        return jsonify(participante), 200
    return jsonify({"error": "Participante no encontrado"}), 404


@participantes_routes.route("/participante/<ci>", methods=["PUT"])
def modificar_participante(ci):
    data = request.json
    nombre = data.get("nombre")
    apellido = data.get("apellido")
    email = data.get("email")

    if not all([nombre, apellido, email]):
        return jsonify({"error": "Faltan datos obligatorios"}), 400

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE participante
        SET nombre = %s,
            apellido = %s,
            email = %s
        WHERE ci = %s
    """, (nombre, apellido, email, ci))
    conn.commit()
    filas_afectadas = cursor.rowcount
    conn.close()

    if filas_afectadas == 0:
        return jsonify({"error": "Participante no encontrado"}), 404

    return jsonify({"mensaje": "Participante actualizado"}), 200


@participantes_routes.route("/participante/<ci>", methods=["DELETE"])
def eliminar_participante(ci):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM participante WHERE ci = %s", (ci,))
    conn.commit()
    filas_afectadas = cursor.rowcount
    conn.close()

    if filas_afectadas == 0:
        return jsonify({"error": "Participante no encontrado"}), 404

    return jsonify({"mensaje": "Participante eliminado"}), 200