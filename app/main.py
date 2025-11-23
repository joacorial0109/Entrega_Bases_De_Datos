from flask import Flask
from flask_cors import CORS

from rutas.login_routes import login_routes
from rutas.participantes_routes import participantes_routes
from rutas.sala_routes import sala_routes
from rutas.reserva_routes import reserva_routes
from rutas.turno_routes import turno_routes
from rutas.edificio_routes import edificio_routes
from rutas.program_routes import program_routes
from rutas.sancion_routes import sancion_routes
from rutas.consultas_routes import consultas_routes

app = Flask(__name__)
CORS(app)

app.register_blueprint(login_routes)
app.register_blueprint(participantes_routes)
app.register_blueprint(sala_routes)
app.register_blueprint(reserva_routes)
app.register_blueprint(turno_routes)
app.register_blueprint(edificio_routes)
app.register_blueprint(program_routes)
app.register_blueprint(sancion_routes)
app.register_blueprint(consultas_routes)

@app.route("/")
def home():
    return "API Funcionando correctamente"

if __name__ == "__main__":
    app.run(debug=True)
