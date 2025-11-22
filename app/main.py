from flask import Flask, jsonify
from flask_cors import CORS

from app.rutas.reserva_routes import reserva_routes
from app.rutas.sala_routes import sala_routes
from app.rutas.participantes_routes import participantes_routes
from app.rutas.program_routes import program_routes
from app.rutas.sancion_routes import sancion_routes
from app.rutas.consultas_routes import consultas_routes

app = Flask(__name__)
CORS(app)

app.register_blueprint(reserva_routes)
app.register_blueprint(sala_routes)
app.register_blueprint(participantes_routes)
app.register_blueprint(program_routes)
app.register_blueprint(sancion_routes)
app.register_blueprint(consultas_routes)

@app.route("/debug/db")
def debug_db():
    import app.db as db
    conn = db.get_connection()
    return {"database": conn.database}

@app.route("/")
def home():
    return jsonify({"mensaje": "API de Gestión de Salas funcionando correctamente"}), 200

if __name__ == "__main__":
    app.run(debug=True)
