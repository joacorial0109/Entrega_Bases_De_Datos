# Entrega_Bases_De_Datos

Instructivo completo para correr la aplicación de forma local

Este instructivo explica cómo ejecutar el sistema de Gestión de Salas UCU de forma local, incluyendo backend (Flask + MySQL), la base de datos y el frontend.

- Requisitos previos:
Tener instalado Python y MySQL.

- Descargar o clonar el proyecto.
Descargar el archivo ZIP o clonarlo con Git y abrir la carpeta del proyecto.

- Instalar dependencias del backend:
Ejecutar en la raíz del proyecto
pip install -r requirements.txt

- Creación de la base de datos:
Abrir MySQL Workbench o DataGrip y ejecutar primero el archivo:
01_create_tables.sql
y luego:
02_insert_data.sql
Estos archivos crean todas las tablas necesarias (participantes, sala, reserva, edificio, programa_academico, etc.) e insertan los datos iniciales.

- Configurar la conexión a MySQL:
Abrir el archivo:
app/db.py
Verificar que los datos (host, user, password, database) coincidan con la configuración local de tu MySQL.

- Ejecutar el backend (Flask):
Desde la raíz del proyecto ejecutar:
python app/main.py

- Ejecutar el frontend:
No requiere servidor. Solo abrir con doble click:
Frontend/login.html

Usuarios de prueba:

Administrador:
usuario: admin@ucu.edu.uy
contraseña: admin123

Estudiante:
usuario: juan@ucu.edu.uy
contraseña: 1234
