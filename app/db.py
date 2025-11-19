# app/db.py
import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Joaco0109/",
        database="gestion_salas"
    )
