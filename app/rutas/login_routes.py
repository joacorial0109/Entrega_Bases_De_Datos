from flask import Blueprint, request, jsonify
from app.db import get_connection

login_routes = Blueprint("login_routes", __name__)

@login_routes.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    usuario = data.get("usuario")
    contrasena = data.get("contrasena")

    if not usuario or not contrasena:
        return jsonify({"error": "Faltan datos"}), 400

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT id_login, usuario
        FROM login
        WHERE usuario = %s AND contrasena = %s
    """, (usuario, contrasena))

    user = cursor.fetchone()

    if not user:
        conn.close()
        return jsonify({"error": "Usuario o contraseña incorrectos"}), 401

    cursor.execute("""
        SELECT ci, nombre, apellido
        FROM participante
        WHERE id_login = %s
    """, (user["id_login"],))

    participante = cursor.fetchone()

    conn.close()

    if participante:
        rol = "usuario"
        ci = participante["ci"]
    else:
        rol = "admin"
        ci = None

    return jsonify({
        "message": "ok",
        "rol": rol,
        "ci": ci,
        "usuario": usuario
    }), 200

@login_routes.route("/login", methods=["PUT"])
def crear_login():
    data = request.get_json()

    usuario = data.get("usuario")
    contrasena = data.get("contrasena")

    if not usuario or not contrasena:
        return jsonify({"error": "Faltan datos"}), 400

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM login WHERE usuario = %s", (usuario,))
    if cursor.fetchone():
        conn.close()
        return jsonify({"error": "El usuario ya existe"}), 409

    cursor.execute("""
        INSERT INTO login (usuario, contrasena)
        VALUES (%s, %s)
    """, (usuario, contrasena))

    conn.commit()
    conn.close()

    return jsonify({"message": "Login creado correctamente"}), 201
