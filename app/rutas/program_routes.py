from flask import Blueprint, jsonify, request
from app.db import get_connection

program_routes = Blueprint('program_routes')

@program_routes.route("/programa", methods=["POST"])
def crear_programa():
    data = request.json
    nombre_programa = data.get("nombre_programa")
    id_facultad = data.get("id_facultad")
    tipo = data.get("tipo")

    if not all([nombre_programa, id_facultad, tipo]):
        return jsonify({"error": "Faltan datos obligatorios"}), 400

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO programa_academico (nombre_programa, id_facultad, tipo)
        VALUES (%s, %s, %s)
    """, (nombre_programa, id_facultad, tipo))
    conn.commit()
    conn.close()
    return jsonify({"mensaje": "Programa creado"}), 201


@program_routes.route("/programas", methods=["GET"])
def listar_programas():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM programa_academico")
    programas = cursor.fetchall()
    conn.close()
    return jsonify(programas), 200


@program_routes.route("/programa/<int:id_programa>", methods=["GET"])
def obtener_programa(id_programa):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM programa_academico WHERE id_programa=%s", (id_programa,))
    programa = cursor.fetchone()
    conn.close()

    if programa:
        return jsonify(programa), 200
    return jsonify({"error": "Programa no encontrado"}), 404


@program_routes.route("/programa/<int:id_programa>", methods=["PUT"])
def modificar_programa(id_programa):
    data = request.json
    nombre_programa = data.get("nombre_programa")
    id_facultad = data.get("id_facultad")
    tipo = data.get("tipo")

    if not all([nombre_programa, id_facultad, tipo]):
        return jsonify({"error": "Faltan datos obligatorios"}), 400

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE programa_academico
        SET nombre_programa=%s, id_facultad=%s, tipo=%s
        WHERE id_programa=%s
    """, (nombre_programa, id_facultad, tipo, id_programa))
    conn.commit()
    filas_afectadas = cursor.rowcount
    conn.close()

    if filas_afectadas == 0:
        return jsonify({"error": "Programa no encontrado"}), 404

    return jsonify({"mensaje": "Programa actualizado"}), 200


@program_routes.route("/programa/<int:id_programa>", methods=["DELETE"])
def eliminar_programa(id_programa):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM programa_academico WHERE id_programa=%s", (id_programa,))
    conn.commit()
    filas_afectadas = cursor.rowcount
    conn.close()

    if filas_afectadas == 0:
        return jsonify({"error": "Programa no encontrado"}), 404

    return jsonify({"mensaje": "Programa eliminado"}), 200