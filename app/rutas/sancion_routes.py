from flask import Blueprint, jsonify, request
from app.db import get_connection

sancion_routes = Blueprint('sancion_routes', __name__)

@sancion_routes.route("/sancion", methods=["POST"])
def crear_sancion():
    data = request.json
    ci_participante = data.get("ci_participante")
    motivo = data.get("motivo")
    fecha = data.get("fecha")

    if not all([ci_participante, motivo, fecha]):
        return jsonify({"error": "Faltan datos obligatorios"}), 400

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO sancion_participante (ci_participante, motivo, fecha)
        VALUES (%s, %s, %s)
    """, (ci_participante, motivo, fecha))
    conn.commit()
    conn.close()
    return jsonify({"mensaje": "Sanción registrada"}), 201
