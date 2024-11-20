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
CSV_ANALISIS_FILE = "registro_analisis.csv"

# Selección de idioma
idioma = st.sidebar.selectbox("Idioma / Language", ["Español", "English"], index=0)

# Función para registrar en CSV
def guardar_registro_csv(nombre, email, numero_economico, file_name, servicios):
    tz_mexico = pytz.timezone("America/Mexico_City")
    fecha_hora = datetime.now(tz_mexico).strftime("%Y-%m-%d %H:%M:%S")
    servicios_str = ", ".join(servicios)

    encabezados = [
        "Fecha y Hora", "Nombre", "Email", "Número Económico",
        "Nombre del Archivo", "Servicios Solicitados", "Estado", "Fecha de Terminación"
    ]
    datos = [fecha_hora, nombre, email, numero_economico, file_name, servicios_str, "Activo", ""]

    try:
        with open(CSV_ANALISIS_FILE, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            if file.tell() == 0:  # Escribe encabezados si el archivo está vacío
                writer.writerow(encabezados)
            writer.writerow(datos)
    except Exception as e:
        st.error(f"Error al guardar el registro en CSV: {e}")

# Función para enviar notificación al administrador
def send_to_admin_with_files(user_file_data, user_file_name):
    try:
        mensaje = MIMEMultipart()
        mensaje['From'] = EMAIL_USER
        mensaje['To'] = NOTIFICATION_EMAIL
        mensaje['Subject'] = "Nuevo archivo recibido - Análisis Estadístico" if idioma == "Español" else "New File Received - Statistical Analysis"

        cuerpo = (
            f"Se ha recibido un nuevo registro en el sistema. Consulta los archivos adjuntos." 
            if idioma == "Español" else 
            "A new record has been added to the system. Check the attached files."
        )
        mensaje.attach(MIMEText(cuerpo, 'plain'))

        # Adjuntar el archivo CSV
        with open(CSV_ANALISIS_FILE, "rb") as attachment:
            part_csv = MIMEBase("application", "octet-stream")
            part_csv.set_payload(attachment.read())
        encoders.encode_base64(part_csv)
        part_csv.add_header("Content-Disposition", f"attachment; filename={CSV_ANALISIS_FILE}")
        mensaje.attach(part_csv)

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
def send_confirmation(email, nombre, servicios):
    try:
        mensaje = MIMEMultipart()
        mensaje['From'] = EMAIL_USER
        mensaje['To'] = email
        mensaje['Subject'] = "Confirmación de recepción" if idioma == "Español" else "Receipt Confirmation"

        cuerpo = (
            f"Hola {nombre}, hemos recibido tu archivo. Servicios solicitados: {', '.join(servicios)}." 
            if idioma == "Español" else 
            f"Hello {nombre}, we have received your file. Requested services: {', '.join(servicios)}."
        )
        mensaje.attach(MIMEText(cuerpo, 'plain'))

        # Enviar correo
        context = ssl.create_default_context()
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls(context=context)
            server.login(EMAIL_USER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_USER, email, mensaje.as_string())
    except Exception as e:
        st.error(f"Error al enviar confirmación al usuario: {e}")

# Añadir logo y título
st.image("escudo_COLOR.jpg", width=100)
st.title("Análisis Estadístico" if idioma == "Español" else "Statistical Analysis")

# Solicitar información del usuario
nombre_completo = st.text_input("Nombre completo" if idioma == "Español" else "Full Name")
numero_economico = st.text_input("Número Económico" if idioma == "Español" else "Id. Number")
email = st.text_input("Correo electrónico" if idioma == "Español" else "Email Address")
email_confirmacion = st.text_input("Confirma tu correo" if idioma == "Español" else "Confirm your email")

# Selección de servicios
opcion_otro = "Otro" if idioma == "Español" else "Other"
servicios_solicitados = st.multiselect(
    "¿Qué servicios de análisis estadístico solicita?" if idioma == "Español" else "Which statistical analysis services do you request?",
    [opcion_otro,
     "Requiero asesoría" if idioma == "Español" else "I require assistance",
     "Normalización de variables" if idioma == "Español" else "Variable Normalization",
     "Asociación de variables" if idioma == "Español" else "Variable Association",
     "Correlación" if idioma == "Español" else "Correlation",
     "Regresión logística" if idioma == "Español" else "Logistic Regression",
     "Regresión lineal y Cox" if idioma == "Español" else "Linear Regression and Cox",
     "Ecuaciones estructurales" if idioma == "Español" else "Structural Equations"]
)

# Campo adicional para "Otro" servicio
otro_servicio = None
if opcion_otro in servicios_solicitados:
    otro_servicio = st.text_input(
        "Por favor, especifique el servicio si seleccionó 'Otro'." if idioma == "Español" else "Please specify the service if you selected 'Other'."
    )

# Subida de archivo
uploaded_file = st.file_uploader(
    "Sube tu archivo (.xls, .xlsx)" if idioma == "Español" else "Upload your file (.xls, .xlsx)", 
    type=["xls", "xlsx"]
)

# Procesar envío
if st.button("Enviar archivo" if idioma == "Español" else "Submit File"):
    if not nombre_completo or not numero_economico or not email or not email_confirmacion or email != email_confirmacion or uploaded_file is None:
        st.error("Por favor, completa todos los campos correctamente." if idioma == "Español" else "Please complete all fields correctly.")
    elif opcion_otro in servicios_solicitados and not otro_servicio:
        st.error("Por favor, especifica el servicio requerido." if idioma == "Español" else "Please specify the required service.")
    else:
        with st.spinner("Enviando..." if idioma == "Español" else "Submitting..."):
            file_data = uploaded_file.getbuffer()
            file_name = uploaded_file.name

            # Incluir el campo adicional si fue especificado
            if otro_servicio and otro_servicio.strip():
                servicios_solicitados.append(otro_servicio.strip())

            # Guardar en registro_analisis.csv
            guardar_registro_csv(nombre_completo, email, numero_economico, file_name, servicios_solicitados)

            # Enviar confirmación al usuario
            send_confirmation(email, nombre_completo, servicios_solicitados)

            # Notificar al administrador con el archivo CSV y el archivo del usuario
            send_to_admin_with_files(file_data, file_name)

            st.success("Envío exitoso. Cierre la aplicación." if idioma == "Español" else "Submission successful. Close the application.")

