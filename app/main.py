from flask import Flask, jsonify
from flask_cors import CORS

# Importar todos los Blueprints
from app.rutas.reserva_routes import reserva_routes
from app.rutas.sala_routes import sala_routes
from app.rutas.participantes_routes import participantes_routes
from app.rutas.program_routes import program_routes
from app.rutas.sancion_routes import sancion_routes
from app.rutas.consultas_routes import consultas_routes

app = Flask(__name__)
CORS(app)

# Registrar los Blueprints
app.register_blueprint(reserva_routes)
app.register_blueprint(sala_routes)
app.register_blueprint(participantes_routes)
app.register_blueprint(program_routes)
app.register_blueprint(sancion_routes)
app.register_blueprint(consultas_routes)

# Ruta raíz
@app.route("/")
def home():
    return jsonify({"mensaje": "API de Gestión de Salas funcionando correctamente"}), 200

# Error handler 404
@app.errorhandler(404)
def no_encontrado(e):
    return jsonify({"error": "Ruta no encontrada"}), 404

# Error handler 500
@app.errorhandler(500)
def error_servidor(e):
    return jsonify({"error": "Error interno del servidor"}), 500

if __name__ == "__main__":
    app.run(debug=True)
