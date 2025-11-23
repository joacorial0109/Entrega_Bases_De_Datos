from flask import Blueprint, request, jsonify
from app.db import get_connection

participantes_routes = Blueprint('participantes_routes', __name__)

@participantes_routes.route("/participantes", methods=["GET"])
def listar_participantes():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT p.ci, p.nombre, p.apellido, p.email,
               COALESCE(pa.tipo, 'sin programa') AS tipo_programa,
               COALESCE(ppa.rol, 'sin rol') AS rol
        FROM participante p
        LEFT JOIN participante_programa_academico ppa ON ppa.ci_participante = p.ci
        LEFT JOIN programa_academico pa ON pa.id_programa = ppa.id_programa
        ORDER BY p.apellido, p.nombre
    """)

    participantes = cursor.fetchall()
    conn.close()

    return jsonify(participantes), 200

@participantes_routes.route("/participante", methods=["POST"])
def crear_participante():
    data = request.get_json()

    ci = data.get("ci")
    nombre = data.get("nombre")
    apellido = data.get("apellido")
    email = data.get("email")
    id_login = data.get("id_login")  # Puede ser null si NO es usuario del sistema
    id_programa = data.get("id_programa")  # Puede ser null
    rol = data.get("rol")  # alumno | docente | admin

    if not all([ci, nombre, apellido, email]):
        return jsonify({"error": "Faltan datos obligatorios"}), 400

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT ci FROM participante WHERE ci = %s", (ci,))
    if cursor.fetchone():
        conn.close()
        return jsonify({"error": "Ya existe un participante con esa CI"}), 409

    cursor.execute("""
        INSERT INTO participante (ci, nombre, apellido, email, id_login)
        VALUES (%s, %s, %s, %s, %s)
    """, (ci, nombre, apellido, email, id_login))

    if id_programa and rol:
        cursor.execute("""
            INSERT INTO participante_programa_academico (ci_participante, id_programa, rol)
            VALUES (%s, %s, %s)
        """, (ci, id_programa, rol))

    conn.commit()
    conn.close()

    return jsonify({"mensaje": "Participante creado correctamente"}), 201

@participantes_routes.route("/participante/<ci>", methods=["GET"])
def obtener_participante(ci):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT p.*, 
               pa.tipo AS tipo_programa,
               ppa.rol AS rol
        FROM participante p
        LEFT JOIN participante_programa_academico ppa ON ppa.ci_participante = p.ci
        LEFT JOIN programa_academico pa ON pa.id_programa = ppa.id_programa
        WHERE p.ci = %s
    """, (ci,))

    participante = cursor.fetchone()
    conn.close()

    if not participante:
        return jsonify({"error": "Participante no encontrado"}), 404

    return jsonify(participante), 200

@participantes_routes.route("/participante/<ci>", methods=["PUT"])
def modificar_participante(ci):
    data = request.get_json()
    nombre = data.get("nombre")
    apellido = data.get("apellido")
    email = data.get("email")
    id_programa = data.get("id_programa")
    rol = data.get("rol")

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM participante WHERE ci = %s", (ci,))
    if not cursor.fetchone():
        conn.close()
        return jsonify({"error": "Participante no encontrado"}), 404

    cursor.execute("""
        UPDATE participante
        SET nombre = %s, apellido = %s, email = %s
        WHERE ci = %s
    """, (nombre, apellido, email, ci))

    if id_programa and rol:
        cursor.execute("""
            DELETE FROM participante_programa_academico
            WHERE ci_participante = %s
        """, (ci,))

        cursor.execute("""
            INSERT INTO participante_programa_academico (ci_participante, id_programa, rol)
            VALUES (%s, %s, %s)
        """, (ci, id_programa, rol))

    conn.commit()
    conn.close()

    return jsonify({"mensaje": "Participante actualizado correctamente"}), 200

@participantes_routes.route("/participante/<ci>", methods=["DELETE"])
def eliminar_participante(ci):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM participante WHERE ci = %s", (ci,))
    if not cursor.fetchone():
        conn.close()
        return jsonify({"error": "Participante no encontrado"}), 404

    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM reserva_participante
        WHERE ci_participante = %s
    """, (ci,))
    if cursor.fetchone()["total"] > 0:
        conn.close()
        return jsonify({"error": "No se puede eliminar porque tiene reservas asociadas"}), 409

    cursor.execute("DELETE FROM participante WHERE ci = %s", (ci,))
    conn.commit()
    conn.close()

    return jsonify({"mensaje": "Participante eliminado correctamente"}), 200
