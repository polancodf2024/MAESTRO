import streamlit as st
from pathlib import Path
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os

# Configuración del servidor de correo
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_USER = "abcdf2024dfabc@gmail.com"
EMAIL_PASSWORD = "hjdd gqaw vvpj hbsy"
NOTIFICATION_EMAIL = "polanco@unam.mx"

# Carpeta temporal para archivos subidos
TEMP_FOLDER = "temp_files"

# Crear la carpeta temporal si no existe
if not os.path.exists(TEMP_FOLDER):
    os.makedirs(TEMP_FOLDER)

# Función para enviar correos con archivo adjunto
def send_email_with_attachment(email_recipient, subject, body, attachment_path):
    mensaje = MIMEMultipart()
    mensaje['From'] = EMAIL_USER
    mensaje['To'] = email_recipient
    mensaje['Subject'] = subject

    # Cuerpo del mensaje
    mensaje.attach(MIMEText(body, 'plain'))

    # Adjuntar archivo correctamente
    try:
        with open(attachment_path, "rb") as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename="{Path(attachment_path).name}"')
            mensaje.attach(part)
    except Exception as e:
        st.error(f"Error al adjuntar el archivo: {e}")

    # Enviar el correo
    context = ssl.create_default_context()
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls(context=context)
            server.login(EMAIL_USER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_USER, email_recipient, mensaje.as_string())
    except Exception as e:
        st.error(f"Error al enviar el correo: {e}")

# Interfaz de Streamlit
st.title("Sistema de Corrección de Estilo")

# Solicitar información del usuario
nombre_completo = st.text_input("Nombre completo del usuario")
numero_economico = st.text_input("Número económico del usuario")
email = st.text_input("Correo electrónico del usuario")
email_confirmacion = st.text_input("Confirma tu correo electrónico")

# Opciones de corrección
st.subheader("Opciones de corrección:")
opciones_correccion = st.multiselect(
    "Selecciona las opciones de corrección que necesitas:",
    ["Revisión de estilo", "Corrección ortotipográfica", "Corrección gramatical", "Formato APA", "Formato MLA"]
)

# Subida del archivo
uploaded_file = st.file_uploader("Sube tu archivo .doc o .docx", type=["doc", "docx"])

if st.button("Enviar archivo"):
    if not nombre_completo or not numero_economico or not email or not email_confirmacion or email != email_confirmacion or not uploaded_file or not opciones_correccion:
        st.error("Por favor, completa todos los campos y sube un archivo.")
    else:
        with st.spinner("Procesando archivo, por favor espera..."):
            try:
                # Guardar el archivo localmente en la carpeta temporal
                file_name = uploaded_file.name
                file_path = os.path.join(TEMP_FOLDER, file_name)
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())

                # Crear cuerpo de correo
                opciones_seleccionadas = ", ".join(opciones_correccion)
                user_subject = "Confirmación de recepción de documento"
                user_body = (
                    f"Hola {nombre_completo},\n\n"
                    f"Hemos recibido tu documento: {file_name}.\n"
                    f"Número económico: {numero_economico}.\n"
                    f"Opciones de corrección solicitadas: {opciones_seleccionadas}."
                )

                admin_subject = "Nuevo archivo recibido - Sistema de Corrección de Estilo"
                admin_body = (
                    f"Se ha recibido un documento de {nombre_completo} ({email}).\n"
                    f"Número económico: {numero_economico}.\n"
                    f"Nombre del archivo: {file_name}.\n"
                    f"Opciones de corrección solicitadas: {opciones_seleccionadas}."
                )

                # Enviar correos
                send_email_with_attachment(email, user_subject, user_body, file_path)
                send_email_with_attachment(NOTIFICATION_EMAIL, admin_subject, admin_body, file_path)

                st.success("Archivo subido y correos enviados correctamente.")
            except Exception as e:
                st.error(f"Error al procesar el archivo: {e}")

