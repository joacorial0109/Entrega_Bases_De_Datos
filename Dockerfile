# Imagen base de Python
FROM python:3.10-slim

# Crear directorio para la app
WORKDIR /app

# Copiar requirements
COPY requirements.txt .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo el proyecto
COPY . .

# Exponer puerto del backend Flask
EXPOSE 5000

# Comando para ejecutar la app
CMD ["python", "app/main.py"]
