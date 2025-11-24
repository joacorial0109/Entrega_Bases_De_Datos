# Entrega_Bases_De_Datos

Instructivo para correr la aplicación localmente

Requisitos:

Python 3.10+

MySQL Server

pip instalado

Descargar el proyecto
Clonar o descargar el ZIP y abrir la carpeta del proyecto.

Instalar dependencias del backend
Ejecutar:
pip install -r requirements.txt

Crear la base de datos
Ejecutar en MySQL Workbench o DataGrip los archivos:
01_create_tables.sql
02_insert_data.sql

Configurar la conexión MySQL
Editar el archivo app/db.py y ajustar los valores:
host, user, password, database.

Ejecutar el backend (Flask)
python app/main.py

Ejecutar el frontend
Abrir directamente el archivo:
Frontend/login.html

Usuarios de prueba:
Administrador: admin@ucu.edu.uy
 / admin123
Estudiante: juan@ucu.edu.uy
 / 1234
