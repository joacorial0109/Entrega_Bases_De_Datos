from flask import Flask

# Importar todos los Blueprints
from app.rutas.reserva_routes import reserva_routes
from app.rutas.sala_routes import sala_routes
from app.rutas.participantes_routes import participantes_routes
from app.rutas.program_routes import program_routes
from app.rutas.sancion_routes import sancion_routes
from app.rutas.consultas_routes import consultas_routes

app = Flask(__name__)

# Registrar los Blueprints
app.register_blueprint(reserva_routes)
app.register_blueprint(sala_routes)
app.register_blueprint(participantes_routes)
app.register_blueprint(program_routes)
app.register_blueprint(sancion_routes)
app.register_blueprint(consultas_routes)

if __name__ == "__main__":
    app.run(debug=True)
