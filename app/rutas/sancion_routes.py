from flask import Blueprint, jsonify, request
from app.db import get_connection

sancion_routes = Blueprint('sancion_routes', __name__)

@sancion_routes.route("/sancion", methods=["POST"])
def crear_sancion():
    data = request.json
    ci_participante = data.get("ci_participante")
    fecha_inicio = data.get("fecha_inicio")
    fecha_fin = data.get("fecha_fin")

    if not all([ci_participante, fecha_inicio, fecha_fin]):
        return jsonify({"error": "Faltan datos obligatorios"}), 400

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO sancion_participante (ci_participante, fecha_inicio, fecha_fin)
        VALUES (%s, %s, %s)
    """, (ci_participante, fecha_inicio, fecha_fin))
    conn.commit()
    conn.close()

    return jsonify({"mensaje": "Sanción registrada"}), 201


@sancion_routes.route("/sanciones", methods=["GET"])
def listar_sanciones():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM sancion_participante")
    sanciones = cursor.fetchall()
    conn.close()
    return jsonify(sanciones), 200


@sancion_routes.route("/sancion/<int:id_sancion>", methods=["GET"])
def obtener_sancion(id_sancion):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM sancion_participante WHERE id_sancion=%s", (id_sancion,))
    sancion = cursor.fetchone()
    conn.close()

    if sancion:
        return jsonify(sancion), 200
    return jsonify({"error": "Sanción no encontrada"}), 404


@sancion_routes.route("/sancion/<int:id_sancion>", methods=["PUT"])
def modificar_sancion(id_sancion):
    data = request.json
    fecha_inicio = data.get("fecha_inicio")
    fecha_fin = data.get("fecha_fin")

    if not all([fecha_inicio, fecha_fin]):
        return jsonify({"error": "Faltan datos obligatorios"}), 400

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE sancion_participante
        SET fecha_inicio=%s, fecha_fin=%s
        WHERE id_sancion=%s
    """, (fecha_inicio, fecha_fin, id_sancion))
    conn.commit()
    filas = cursor.rowcount
    conn.close()

    if filas == 0:
        return jsonify({"error": "Sanción no encontrada"}), 404

    return jsonify({"mensaje": "Sanción actualizada"}), 200


@sancion_routes.route("/sancion/<int:id_sancion>", methods=["DELETE"])
def eliminar_sancion(id_sancion):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM sancion_participante WHERE id_sancion=%s", (id_sancion,))
    conn.commit()
    filas = cursor.rowcount
    conn.close()

    if filas == 0:
        return jsonify({"error": "Sanción no encontrada"}), 404

    return jsonify({"mensaje": "Sanción eliminada"}), 200