import streamlit as st
import os
from pathlib import Path
import pandas as pd
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import csv

# Configuración
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_USER = "abcdf2024dfabc@gmail.com"
EMAIL_PASSWORD = "hjdd gqaw vvpj hbsy"
CSV_FILE = "/mount/src/maestro/registro_convocatorias.csv"


# Solicitar contraseña al inicio
PASSWORD = "Tt5plco5"
input_password = st.text_input("Ingresa la contraseña para acceder:", type="password")

# Verificar la contraseña
if input_password != PASSWORD:
    st.error("Escribe la contraseña correcta, y presiona ENTER.")

    st.stop()


# Función para enviar el PDF como adjunto
def enviar_pdf_adjuntos(pdf_path):
    try:
        # Leer la lista de correos electrónicos del archivo CSV
        df = pd.read_csv(CSV_FILE)

        # Filtrar registros con estado "Activo"
        registros_activos = df[df["Estado"] == "Activo"]

        # Verificar si hay correos registrados con estado activo
        if registros_activos.empty:
            st.warning("No hay correos registrados con estado 'Activo'.")
            return

        # Iterar sobre los registros para personalizar el correo
        for index, registro in registros_activos.iterrows():
            correo = registro["Correo Electrónico"]
            nombre = registro["Nombre Completo"]

            # Crear un nuevo mensaje para cada destinatario
            mensaje = MIMEMultipart()
            mensaje['From'] = EMAIL_USER
            mensaje['To'] = correo
            mensaje['Subject'] = "Envío de Convocatoria Adjunta"

            # Personalizar el cuerpo del correo
            cuerpo = (
                f"Estimado/a {nombre},\n\n"
                "Adjunto encontrará el PDF de la convocatoria.\n\n"
                "Saludos cordiales."
            )
            mensaje.attach(MIMEText(cuerpo, 'plain'))

            # Adjuntar el archivo PDF
            with open(pdf_path, "rb") as pdf_file:
                adjunto = MIMEApplication(pdf_file.read(), _subtype="pdf")
                adjunto.add_header('Content-Disposition', 'attachment', filename="convocatoria.pdf")
                mensaje.attach(adjunto)

            # Configurar la conexión SMTP
            context = ssl.create_default_context()
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls(context=context)
                server.login(EMAIL_USER, EMAIL_PASSWORD)

                # Enviar el correo
                server.sendmail(EMAIL_USER, correo, mensaje.as_string())

        st.success("Archivo PDF enviado exitosamente a todos los correos registrados con estado 'Activo'.")

    except Exception as e:
        st.error("Error al enviar el archivo PDF.")
        st.error(str(e))

# Función para subir y reemplazar el archivo CSV
def subir_csv(uploaded_csv):
    try:
        temp_file = "temp_interesados.csv"
        with open(temp_file, "wb") as f:
            f.write(uploaded_csv.getbuffer())

        # Reemplazar el archivo existente
        os.system(f"cp {temp_file} {CSV_FILE}")
        st.success("Archivo registro_convocatorias.csv subido y reemplazado exitosamente.")

        # Mostrar una vista previa del archivo subido
        df = pd.read_csv(CSV_FILE)
        st.dataframe(df)

        # Eliminar el archivo temporal
        os.remove(temp_file)
    except Exception as e:
        st.error("Error al subir el archivo CSV.")
        st.error(str(e))

# Función para descargar el archivo CSV
def descargar_csv():
    if Path(CSV_FILE).exists():
        with open(CSV_FILE, "rb") as file:
            st.download_button(
                label="Descargar registro_convocatorias.csv",
                data=file,
                file_name="/mount/src/maestro/registro_convocatorias.csv",
                mime="text/csv"
            )
    else:
        st.warning("El archivo registro_convocatorias.csv no existe.")

# Interfaz de Streamlit
st.image("escudo_COLOR.jpg", width=150)
st.title("Gestión de Convocatorias")

# Opción 1: Subir el archivo CSV
st.header("Subir el archivo registro_convocatorias.csv")
uploaded_csv = st.file_uploader("Selecciona el archivo para subir y reemplazar el existente", type=["csv"])
if uploaded_csv:
    subir_csv(uploaded_csv)

# Opción 2: Descargar el archivo CSV
st.header("Descargar el archivo registro_convocatorias.csv")
descargar_csv()

# Opción 3: Enviar PDF personalizado
st.header("Enviar PDF a los correos registrados")
uploaded_pdf = st.file_uploader("Selecciona un archivo PDF para enviar a todos los correos registrados", type=["pdf"])
if uploaded_pdf:
    temp_pdf = "temp_convocatoria.pdf"
    with open(temp_pdf, "wb") as f:
        f.write(uploaded_pdf.getbuffer())
    if st.button("Enviar PDF a todos los correos"):
        enviar_pdf_adjuntos(temp_pdf)
        os.remove(temp_pdf)

