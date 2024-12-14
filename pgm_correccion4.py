import streamlit as st
from pathlib import Path
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import sqlite3
from datetime import datetime
import pytz
import os
import requests
import base64

# Configuración
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_USER = "abcdf2024dfabc@gmail.com"
EMAIL_PASSWORD = "hjdd gqaw vvpj hbsy"
NOTIFICATION_EMAIL = "polanco@unam.mx"
GITHUB_REPO_URL = "https://api.github.com/repos/polancodf2024/MAESTRO/contents/registro_correccion.sqlite"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")  # Token tomado de las variables de entorno
LOCAL_DB_FILE = "registro_correccion.sqlite"

# Descargar base de datos desde GitHub
def descargar_base_datos():
    try:
        if not os.path.exists(LOCAL_DB_FILE):
            headers = {"Authorization": f"token {GITHUB_TOKEN}"}
            response = requests.get(GITHUB_REPO_URL, headers=headers)
            if response.status_code == 200:
                content = base64.b64decode(response.json().get("content", ""))
                with open(LOCAL_DB_FILE, "wb") as f:
                    f.write(content)
                st.write("Base de datos descargada con éxito.")
            else:
                st.error(f"Error al descargar la base de datos: {response.status_code} - {response.text}")
    except Exception as e:
        st.error(f"Error inesperado al descargar la base de datos: {e}")

# Subir base de datos actualizada a GitHub
def subir_base_datos():
    try:
        with open(LOCAL_DB_FILE, "rb") as f:
            content = base64.b64encode(f.read()).decode("utf-8")

        headers = {"Authorization": f"token {GITHUB_TOKEN}"}

        # Obtener SHA
        response = requests.get(GITHUB_REPO_URL, headers=headers)
        sha = response.json().get("sha") if response.status_code == 200 else None

        # Subir archivo
        data = {"message": "Actualizar base de datos", "content": content, "sha": sha}
        response = requests.put(GITHUB_REPO_URL, headers=headers, json=data)

        if response.status_code in [200, 201]:
            st.write("Base de datos subida con éxito.")
        else:
            st.error(f"Error al subir la base de datos: {response.status_code} - {response.text}")
    except Exception as e:
        st.error(f"Error inesperado al subir la base de datos: {e}")

# Crear base de datos y tabla si no existen
def setup_database():
    try:
        conn = sqlite3.connect(LOCAL_DB_FILE)
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS registro_correccion (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha_hora TEXT NOT NULL,
            nombre TEXT NOT NULL,
            email TEXT NOT NULL,
            numero_economico TEXT NOT NULL,
            file_name TEXT NOT NULL,
            servicios TEXT NOT NULL,
            estado TEXT DEFAULT 'Activo',
            fecha_terminacion TEXT
        )
        """)
        conn.commit()
        conn.close()
        st.write("Base de datos configurada correctamente.")
    except Exception as e:
        st.error(f"Error al configurar la base de datos: {e}")

# Función para registrar en la base de datos
def guardar_registro_sqlite(nombre, email, numero_economico, file_name, servicios):
    try:
        tz_mexico = pytz.timezone("America/Mexico_City")
        fecha_hora = datetime.now(tz_mexico).strftime("%Y-%m-%d %H:%M:%S")
        servicios_str = ", ".join(servicios)

        conn = sqlite3.connect(LOCAL_DB_FILE)
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO registro_correccion (fecha_hora, nombre, email, numero_economico, file_name, servicios)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (fecha_hora, nombre, email, numero_economico, file_name, servicios_str))
        conn.commit()
        conn.close()
        st.write("Registro guardado en la base de datos.")
    except Exception as e:
        st.error(f"Error al guardar el registro en la base de datos: {e}")

# Función para enviar notificación al administrador
def send_to_admin_with_files(user_file_data, user_file_name):
    try:
        mensaje = MIMEMultipart()
        mensaje['From'] = EMAIL_USER
        mensaje['To'] = NOTIFICATION_EMAIL
        mensaje['Subject'] = "Nuevo archivo recibido - Corrección de Estilo"

        cuerpo = "Se ha recibido un nuevo registro en el sistema. Consulta los archivos adjuntos."
        mensaje.attach(MIMEText(cuerpo, 'plain'))

        # Adjuntar el archivo del usuario
        part_user_file = MIMEBase("application", "octet-stream")
        part_user_file.set_payload(user_file_data)
        encoders.encode_base64(part_user_file)
        part_user_file.add_header("Content-Disposition", f"attachment; filename={user_file_name}")
        mensaje.attach(part_user_file)

        # Enviar correo
        context = ssl.create_default_context()
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls(context=context)
            server.login(EMAIL_USER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_USER, NOTIFICATION_EMAIL, mensaje.as_string())
    except Exception as e:
        st.error(f"Error al enviar notificación al administrador: {e}")

# Función para enviar confirmación al usuario
def send_confirmation(email, nombre, servicios, user_file_data, user_file_name):
    try:
        mensaje = MIMEMultipart()
        mensaje['From'] = EMAIL_USER
        mensaje['To'] = email
        mensaje['Subject'] = "Confirmación de recepción"

        cuerpo = f"Hola {nombre}, hemos recibido tu archivo. Servicios solicitados: {', '.join(servicios)}."
        mensaje.attach(MIMEText(cuerpo, 'plain'))

        # Configurar el archivo adjunto correctamente
        part_user_file = MIMEBase("application", "octet-stream")
        part_user_file.set_payload(user_file_data)
        encoders.encode_base64(part_user_file)
        part_user_file.add_header("Content-Disposition", f"attachment; filename={user_file_name}")
        mensaje.attach(part_user_file)

        # Enviar correo
        context = ssl.create_default_context()
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls(context=context)
            server.login(EMAIL_USER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_USER, email, mensaje.as_string())
        st.success("Correo de confirmación enviado al usuario.")
    except Exception as e:
        st.error(f"Error al enviar confirmación al usuario: {e}")

# Añadir logo y título
if os.path.exists("escudo_COLOR.jpg"):
    st.image("escudo_COLOR.jpg", width=100)
else:
    st.warning("Imagen no encontrada: escudo_COLOR.jpg")

st.title("Corrección de Estilo")

# Solicitar información del usuario
nombre_completo = st.text_input("Nombre completo")
numero_economico = st.text_input("Número Económico")
email = st.text_input("Correo electrónico")
email_confirmacion = st.text_input("Confirma tu correo")

# Selección de servicios
opcion_otro = "Otro"
servicios_solicitados = st.multiselect(
    "¿Qué servicios de corrección solicita?",
    [opcion_otro, "Revisión de estilo", "Parafraseo", "Reporte de similitud", "Traducción parcial"]
)

# Campo adicional para "Otro" servicio
otro_servicio = None
if opcion_otro in servicios_solicitados:
    otro_servicio = st.text_input("Por favor, especifique el servicio si seleccionó 'Otro'.")

# Subida de archivo
uploaded_file = st.file_uploader("Sube tu archivo (.doc, .docx)", type=["doc", "docx"])

# Procesar envío
if st.button("Enviar archivo"):
    if not nombre_completo or not numero_economico or not email or not email_confirmacion or email != email_confirmacion or uploaded_file is None:
        st.error("Por favor, completa todos los campos correctamente.")
    elif opcion_otro in servicios_solicitados and not otro_servicio:
        st.error("Por favor, especifica el servicio requerido.")
    else:
        with st.spinner("Enviando..."):
            file_data = uploaded_file.getbuffer()
            file_name = uploaded_file.name

            if otro_servicio and otro_servicio.strip():
                servicios_solicitados.append(otro_servicio.strip())

            guardar_registro_sqlite(nombre_completo, email, numero_economico, file_name, servicios_solicitados)
            send_confirmation(email, nombre_completo, servicios_solicitados, file_data, file_name)
            send_to_admin_with_files(file_data, file_name)
            subir_base_datos()

            st.success("Envío exitoso. Cierre la aplicación.")

# Inicializar configuraciones
st.write("Iniciando configuración de la base de datos...")
setup_database()
st.write("Configuración de la base de datos completada.")

st.write("Descargando base de datos...")
descargar_base_datos()
st.write("Descarga de la base de datos completada.")

