from flask import Blueprint, jsonify, request
from app.db import get_connection

program_routes = Blueprint('program_routes', __name__)

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
    return jsonify({"mensaje": "Programa académico creado"}), 201
