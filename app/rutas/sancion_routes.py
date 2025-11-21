from flask import Blueprint, request, jsonify
from app.db import get_connection

sancion_routes = Blueprint('sancion_routes', __name__)

@sancion_routes.route("/sanciones", methods=["GET"])
def obtener_sanciones():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM sancion_participante")
    sanciones = cursor.fetchall()
    conn.close()
    return jsonify(sanciones), 200


@sancion_routes.route("/sanciones/<int:id_sancion>", methods=["GET"])
def obtener_sancion_por_id(id_sancion):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM sancion_participante WHERE id_sancion = %s", (id_sancion,)
    )
    sancion = cursor.fetchone()
    conn.close()

    if sancion:
        return jsonify(sancion), 200
    else:
        return jsonify({"error": "Sanción no encontrada"}), 404


@sancion_routes.route("/sanciones/ci/<ci_participante>", methods=["GET"])
def obtener_sanciones_por_ci(ci_participante):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM sancion_participante WHERE ci_participante = %s",
        (ci_participante,),
    )
    sanciones = cursor.fetchall()
    conn.close()
    return jsonify(sanciones), 200


@sancion_routes.route("/sanciones", methods=["POST"])
def crear_sancion():
    data = request.get_json()
    ci_participante = data.get("ci_participante")
    fecha_inicio = data.get("fecha_inicio")
    fecha_fin = data.get("fecha_fin")

    if not all([ci_participante, fecha_inicio, fecha_fin]):
        return jsonify({"error": "Faltan datos obligatorios"}), 400

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT ci FROM participante WHERE ci = %s", (ci_participante,)
    )
    participante = cursor.fetchone()
    if not participante:
        conn.close()
        return jsonify({"error": "El participante no existe"}), 404

    cursor.execute(
        """
        SELECT id_sancion
        FROM sancion_participante
        WHERE ci_participante = %s
          AND fecha_inicio <= %s
          AND fecha_fin >= %s
        """,
        (ci_participante, fecha_fin, fecha_inicio),
    )
    sancion_existente = cursor.fetchone()
    if sancion_existente:
        conn.close()
        return jsonify(
            {"error": "El participante ya tiene una sanción activa en ese período"}
        ), 409

    cursor.execute(
        """
        INSERT INTO sancion_participante (ci_participante, fecha_inicio, fecha_fin)
        VALUES (%s, %s, %s)
        """,
        (ci_participante, fecha_inicio, fecha_fin),
    )
    conn.commit()
    conn.close()

    return jsonify({"message": "Sanción creada"}), 201


@sancion_routes.route("/sanciones/<int:id_sancion>", methods=["DELETE"])
def eliminar_sancion(id_sancion):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM sancion_participante WHERE id_sancion = %s", (id_sancion,)
    )
    conn.commit()
    filas = cursor.rowcount
    conn.close()

    if filas == 0:
        return jsonify({"error": "No se pudo eliminar la sanción"}), 404

    return jsonify({"message": "Sanción eliminada"}), 200