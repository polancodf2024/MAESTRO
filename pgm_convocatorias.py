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

# Configuración
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_USER = "abcdf2024dfabc@gmail.com"
EMAIL_PASSWORD = "hjdd gqaw vvpj hbsy"
NOTIFICATION_EMAIL = "polanco@unam.mx"
CSV_CONVOCATORIAS_FILE = "registro_convocatorias.csv"

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

# Función para enviar confirmación al usuario
def enviar_confirmacion_usuario(correo, nombre):
    try:
        mensaje = MIMEMultipart()
        mensaje['From'] = EMAIL_USER
        mensaje['To'] = correo
        mensaje['Subject'] = "Confirmación de suscripción" if idioma == "Español" else "Subscription Confirmation"

        cuerpo = (
            f"Hola {nombre},\n\nTu suscripción ha sido recibida exitosamente. Gracias por participar.\n\nSaludos cordiales." 
            if idioma == "Español" else 
            f"Hello {nombre},\n\nYour subscription has been successfully received. Thank you for participating.\n\nBest regards."
        )
        mensaje.attach(MIMEText(cuerpo, 'plain'))

        # Enviar correo
        context = ssl.create_default_context()
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls(context=context)
            server.login(EMAIL_USER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_USER, correo, mensaje.as_string())
    except Exception as e:
        st.error(f"Error al enviar confirmación al usuario: {e}")

# Función para enviar aviso al administrador
def enviar_aviso_administrador():
    try:
        mensaje = MIMEMultipart()
        mensaje['From'] = EMAIL_USER
        mensaje['To'] = NOTIFICATION_EMAIL
        mensaje['Subject'] = "Nuevo registro en convocatorias"

        cuerpo = (
            "Se ha registrado un nuevo usuario en el sistema. Consulta el archivo adjunto para más detalles."
            if idioma == "Español" else 
            "A new user has been registered in the system. Check the attached file for more details."
        )
        mensaje.attach(MIMEText(cuerpo, 'plain'))

        # Adjuntar el archivo CSV
        with open(CSV_CONVOCATORIAS_FILE, "rb") as attachment:
            part_csv = MIMEBase("application", "octet-stream")
            part_csv.set_payload(attachment.read())
        encoders.encode_base64(part_csv)
        part_csv.add_header('Content-Disposition', f'attachment; filename={CSV_CONVOCATORIAS_FILE}')
        mensaje.attach(part_csv)

        # Enviar correo
        context = ssl.create_default_context()
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls(context=context)
            server.login(EMAIL_USER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_USER, NOTIFICATION_EMAIL, mensaje.as_string())
    except Exception as e:
        st.error(f"Error al enviar aviso al administrador: {e}")

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

            # Enviar confirmación al usuario
            enviar_confirmacion_usuario(correo_electronico, nombre_completo)

            # Enviar aviso al administrador con el archivo adjunto
            enviar_aviso_administrador()

            st.success("Registro exitoso, confirmación enviada y administrador notificado." if idioma == "Español" else "Registration successful, confirmation sent, and administrator notified.")

