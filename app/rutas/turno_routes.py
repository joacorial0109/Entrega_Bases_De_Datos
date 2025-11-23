from flask import Blueprint, jsonify
from app.db import get_connection

turno_routes = Blueprint('turno_routes', __name__)

@turno_routes.route("/turnos", methods=["GET"])
def obtener_turnos():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM turno ORDER BY hora_inicio")
    turnos = cursor.fetchall()

    conn.close()

    for t in turnos:
        if hasattr(t["hora_inicio"], "seconds"):
            segundos = t["hora_inicio"].seconds
            t["hora_inicio"] = f"{segundos//3600:02d}:{(segundos%3600)//60:02d}:00"

        if hasattr(t["hora_fin"], "seconds"):
            segundos = t["hora_fin"].seconds
            t["hora_fin"] = f"{segundos//3600:02d}:{(segundos%3600)//60:02d}:00"

    return jsonify(turnos), 200
