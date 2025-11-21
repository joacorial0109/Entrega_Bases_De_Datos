from flask import Blueprint, jsonify, request
from app.db import get_connection

consultas_routes = Blueprint('consultas_routes')


@consultas_routes.route("/participante/<ci>/historial", methods=["GET"])
def historial_participante(ci):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT r.id_reserva, r.fecha, r.id_turno, r.estado, s.nombre_sala
        FROM reserva r
        JOIN reserva_participante rp ON rp.id_reserva = r.id_reserva
        JOIN sala s ON s.id_sala = r.id_sala
        WHERE rp.ci_participante=%s
        ORDER BY r.fecha DESC, r.id_turno
    """, (ci,))

    resultado = cursor.fetchall()
    conn.close()
    return jsonify(resultado), 200


@consultas_routes.route("/participante/<ci>/reservas-activas", methods=["GET"])
def reservas_activas_participante(ci):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT r.id_reserva, r.fecha, r.id_turno, r.estado, s.nombre_sala
        FROM reserva r
        JOIN reserva_participante rp ON rp.id_reserva = r.id_reserva
        JOIN sala s ON s.id_sala = r.id_sala
        WHERE rp.ci_participante=%s AND r.estado='activa'
        ORDER BY r.fecha, r.id_turno
    """, (ci,))

    resultado = cursor.fetchall()
    conn.close()
    return jsonify(resultado), 200


@consultas_routes.route("/sala/<int:id_sala>/reservas", methods=["GET"])
def reservas_por_sala(id_sala):
    fecha = request.args.get("fecha")

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT r.id_reserva, r.fecha, r.id_turno, r.estado
        FROM reserva r
        WHERE r.id_sala=%s AND r.fecha=%s
        ORDER BY r.id_turno
    """, (id_sala, fecha))

    resultado = cursor.fetchall()
    conn.close()
    return jsonify(resultado), 200


@consultas_routes.route("/reservas/filtro", methods=["GET"])
def reservas_filtradas():
    fecha = request.args.get("fecha")
    estado = request.args.get("estado")
    id_sala = request.args.get("id_sala")
    id_turno = request.args.get("id_turno")

    filtros = []
    valores = []

    if fecha:
        filtros.append("r.fecha = %s")
        valores.append(fecha)

    if estado:
        filtros.append("r.estado = %s")
        valores.append(estado)

    if id_sala:
        filtros.append("r.id_sala = %s")
        valores.append(id_sala)

    if id_turno:
        filtros.append("r.id_turno = %s")
        valores.append(id_turno)

    where = " AND ".join(filtros) if filtros else "1=1"

    query = f"""
        SELECT r.id_reserva, r.fecha, r.id_turno, r.estado, s.nombre_sala
        FROM reserva r
        JOIN sala s ON s.id_sala = r.id_sala
        WHERE {where}
        ORDER BY r.fecha, r.id_turno
    """

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query, tuple(valores))
    resultado = cursor.fetchall()
    conn.close()

    return jsonify(resultado), 200