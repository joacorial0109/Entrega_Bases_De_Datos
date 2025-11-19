import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",               # Cambiá si tenés otro usuario
        password="Joaco0109/",           # Cambiá si tenés otra contraseña
        database="gestion_salas"
    )
