import streamlit as st
from pathlib import Path
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import csv
from datetime import datetime
import pytz
import pandas as pd

# Configuración
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_USER = "abcdf2024dfabc@gmail.com"
EMAIL_PASSWORD = "hjdd gqaw vvpj hbsy"
NOTIFICATION_EMAIL = "polanco@unam.mx"
CSV_CONVOCATORIAS_FILE = Path("/mount/src/maestro/registro_convocatorias.csv")

# Selección de idioma
idioma = st.sidebar.selectbox("Idioma", ["Español", "English"], index=0)

# Función para registrar datos en CSV con el formato correcto
def registrar_convocatoria(nombre, correo, numero_economico):
    tz_mexico = pytz.timezone("America/Mexico_City")
    fecha_actual = datetime.now(tz_mexico)

    # Formato de fecha y hora como "2024-11-20 14:55:35"
    fecha_hora = fecha_actual.strftime("%Y-%m-%d %H:%M:%S")

    estado = "Activo"
    fecha_terminacion = ""

    # Encabezados y datos del registro
    encabezados = [
        "Fecha y Hora", "Nombre Completo", "Correo Electronico", 
        "Numero Economico", "Estado", "Fecha de Terminacion"
    ]
    datos = [
        fecha_hora, nombre, correo, numero_economico, estado, fecha_terminacion
    ]

    # Guardar en el archivo CSV
    try:
        with open(CSV_CONVOCATORIAS_FILE, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            if file.tell() == 0:  # Si el archivo está vacío, escribe los encabezados
                writer.writerow(encabezados)
            writer.writerow(datos)
    except Exception as e:
        st.error(f"Error al registrar convocatoria: {e}")

# Función para mostrar contenido del archivo CSV
def mostrar_contenido_csv():
    try:
        if CSV_CONVOCATORIAS_FILE.exists():
            df = pd.read_csv(CSV_CONVOCATORIAS_FILE)
            st.subheader("Contenido del archivo CSV:")
            st.dataframe(df)
        else:
            st.warning("El archivo registro_convocatorias.csv no existe.")
    except Exception as e:
        st.error(f"Error al leer el archivo CSV: {e}")

# Añadir logo y título
st.image("escudo_COLOR.jpg", width=100)
st.title("Registro Para Recibir Convocatorias" if idioma == "Español" else "Registro Para Recibir Convocatorias")

# Solicitar información del usuario
nombre_completo = st.text_input("Nombre completo" if idioma == "Español" else "Full Name")
correo_electronico = st.text_input("Correo Electrónico" if idioma == "Español" else "Email")
correo_electronico_confirmacion = st.text_input("Confirma tu Correo Electrónico" if idioma == "Español" else "Confirm Your Email")
numero_economico = st.text_input("Número Económico" if idioma == "Español" else "Id. Number")

# Procesar envío
if st.button("Enviar" if idioma == "Español" else "Submit"):
    if not nombre_completo or not correo_electronico or not correo_electronico_confirmacion or not numero_economico:
        st.error("Por favor, completa todos los campos correctamente." if idioma == "Español" else "Please complete all fields correctly.")
    elif correo_electronico != correo_electronico_confirmacion:
        st.error("Los correos electrónicos no coinciden." if idioma == "Español" else "Email addresses do not match.")
    else:
        with st.spinner("Registrando..." if idioma == "Español" else "Registering..."):
            # Registrar en el archivo CSV
            registrar_convocatoria(nombre_completo, correo_electronico, numero_economico)
            st.success("Registro exitoso." if idioma == "Español" else "Registration successful.")

# Mostrar contenido del archivo CSV
if st.button("Mostrar contenido del CSV" if idioma == "Español" else "Show CSV Content"):
    mostrar_contenido_csv()

