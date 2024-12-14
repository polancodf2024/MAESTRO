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
GITHUB_TOKEN = "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"  # Token explícito
LOCAL_DB_FILE = "registro_correccion.sqlite"

# Descargar base de datos desde GitHub
def descargar_base_datos():
    try:
        if not os.path.exists(LOCAL_DB_FILE):
            headers = {"Authorization": f"token {GITHUB_TOKEN}"}
            response = requests.get(GITHUB_REPO_URL, headers=headers)
            st.write(f"Headers enviados: {headers}")
            st.write(f"Respuesta completa: {response.text}")
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

        # Datos para la solicitud
        data = {
            "message": "Actualizar base de datos",
            "content": content,
            "sha": "ea19036cef322812e9490a30b13e596ab1558d5e"  # SHA obtenido
        }

        # Solicitud PUT
        response = requests.put(GITHUB_REPO_URL, headers=headers, json=data)

        st.write(f"Headers enviados: {headers}")
        st.write(f"Datos enviados: {data}")
        st.write(f"Respuesta completa: {response.text}")

        if response.status_code in [200, 201]:
            st.success("Base de datos subida con éxito.")
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

# Añadir logo y título
if os.path.exists("escudo_COLOR.jpg"):
    st.image("escudo_COLOR.jpg", width=100)
else:
    st.warning("Imagen no encontrada: escudo_COLOR.jpg")

st.title("Corrección de Estilo")

# Inicializar configuraciones
st.write("Iniciando configuración de la base de datos...")
setup_database()
st.write("Configuración de la base de datos completada.")

st.write("Descargando base de datos...")
descargar_base_datos()
st.write("Descarga de la base de datos completada.")

