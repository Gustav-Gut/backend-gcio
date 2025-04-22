# Usamos la imagen oficial de Python 3.13.2
FROM python:3.13.2

# Establecemos el directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema para compilar mysqlclient
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    build-essential \
    netcat-openbsd

# Copiar el archivo de requerimientos e instalar las dependencias de Python
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copiar el resto del código de la aplicación
COPY . .

# Exponer el puerto en el que correrá Django
EXPOSE 8000

# Comando por defecto
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
