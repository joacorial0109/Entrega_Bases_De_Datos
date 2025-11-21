from flask import Blueprint, request, jsonify
from app.db import get_connection

sancion_routes = Blueprint('sancion_routes')


@sancion_routes.route("/sanciones", methods=["GET"])
def listar_sanciones():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM sancion_participante")
    data = cursor.fetchall()
    conn.close()
    return jsonify(data), 200


@sancion_routes.route("/sanciones/<int:id_sancion>", methods=["GET"])
def obtener_sancion(id_sancion):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM sancion_participante WHERE id_sancion=%s", (id_sancion,))
    data = cursor.fetchone()
    conn.close()
    if not data:
        return jsonify({"error": "Sanción no encontrada"}), 404
    return jsonify(data), 200


@sancion_routes.route("/sanciones", methods=["POST"])
def crear_sancion():
    data = request.json
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO sancion_participante (ci_participante, fecha_inicio, fecha_fin)
        VALUES (%s, %s, %s)
    """, (data["ci_participante"], data["fecha_inicio"], data["fecha_fin"]))
    conn.commit()
    conn.close()
    return jsonify({"mensaje": "Sanción creada correctamente"}), 201


@sancion_routes.route("/sanciones/<int:id_sancion>", methods=["PUT"])
def actualizar_sancion(id_sancion):
    data = request.json
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE sancion_participante
        SET ci_participante=%s, fecha_inicio=%s, fecha_fin=%s
        WHERE id_sancion=%s
    """, (data["ci_participante"], data["fecha_inicio"], data["fecha_fin"], id_sancion))
    conn.commit()
    conn.close()
    return jsonify({"mensaje": "Sanción actualizada correctamente"}), 200


@sancion_routes.route("/sanciones/<int:id_sancion>", methods=["DELETE"])
def eliminar_sancion(id_sancion):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM sancion_participante WHERE id_sancion=%s", (id_sancion,))
    conn.commit()
    conn.close()
    return jsonify({"mensaje": "Sanción eliminada correctamente"}), 200


@sancion_routes.route("/participante/<ci>/sanciones", methods=["GET"])
def obtener_sanciones_participante(ci):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT id_sancion, ci_participante, fecha_inicio, fecha_fin
        FROM sancion_participante
        WHERE ci_participante=%s
        ORDER BY fecha_inicio DESC
    """, (ci,))
    sanciones = cursor.fetchall()
    conn.close()
    return jsonify(sanciones), 200