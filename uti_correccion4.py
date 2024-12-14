import streamlit as st
import sqlite3
import pandas as pd
import os
import requests
import base64

# Configuración de la base de datos y GitHub
GITHUB_REPO_URL = "https://api.github.com/repos/usuario/repositorio/contents/registro_correccion.sqlite"
GITHUB_TOKEN = "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"
DB_FILE = "registro_correccion.sqlite"
PASSWORD = "Tt5plco5"

# Descargar base de datos desde GitHub
def descargar_base_datos():
    if not os.path.exists(DB_FILE):
        headers = {"Authorization": f"token {GITHUB_TOKEN}"}
        response = requests.get(GITHUB_REPO_URL, headers=headers)
        if response.status_code == 200:
            content = base64.b64decode(response.json()["content"])
            with open(DB_FILE, "wb") as f:
                f.write(content)
            print("Base de datos descargada con éxito desde GitHub.")
        else:
            st.error(f"Error al descargar la base de datos: {response.status_code}")

# Subir base de datos actualizada a GitHub
def subir_base_datos():
    with open(DB_FILE, "rb") as f:
        content = base64.b64encode(f.read()).decode("utf-8")

    headers = {"Authorization": f"token {GITHUB_TOKEN}"}

    # Obtener SHA del archivo existente
    response = requests.get(GITHUB_REPO_URL, headers=headers)
    if response.status_code == 200:
        sha = response.json()["sha"]
    else:
        sha = None

    # Subir archivo
    data = {
        "message": "Actualizar base de datos",
        "content": content,
        "sha": sha
    }
    response = requests.put(GITHUB_REPO_URL, headers=headers, json=data)
    if response.status_code in [200, 201]:
        print("Base de datos subida con éxito a GitHub.")
    else:
        st.error(f"Error al subir la base de datos: {response.status_code}")

# Descargar la base de datos al inicio
descargar_base_datos()

# Solicitar contraseña al inicio
input_password = st.text_input("Ingresa la contraseña para acceder:", type="password")

# Verificar la contraseña
if input_password != PASSWORD:
    st.error("Escribe la contraseña correcta, y presiona ENTER.")
    st.stop()

# Mostrar el logo del escudo
st.image("escudo_COLOR.jpg", width=150)

# Título de la aplicación
st.title("Gestión de Base de Datos: registro_correccion")

# Función para leer datos desde SQLite
def leer_datos_sqlite():
    try:
        conn = sqlite3.connect(DB_FILE)
        query = "SELECT * FROM registro_correccion"
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Error al leer los datos: {e}")
        return pd.DataFrame()

# Función para reemplazar los datos en la base de datos
def reemplazar_datos_sqlite(df):
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        # Eliminar los datos existentes
        cursor.execute("DELETE FROM registro_correccion")

        # Insertar los nuevos datos
        df.to_sql("registro_correccion", conn, if_exists="append", index=False)

        conn.commit()
        conn.close()
        st.success("Datos reemplazados exitosamente en la base de datos.")
        subir_base_datos()
    except Exception as e:
        st.error(f"Error al reemplazar los datos: {e}")

# Opción para subir el archivo de análisis
st.header("Subir los datos a la base de datos")
uploaded_csv = st.file_uploader("Selecciona un archivo CSV para cargar en la base de datos", type=["csv"])

if uploaded_csv is not None:
    try:
        # Leer el archivo subido
        df_nuevo = pd.read_csv(uploaded_csv)

        # Mostrar una vista previa del archivo subido
        st.subheader("Vista previa del archivo subido:")
        st.dataframe(df_nuevo)

        # Botón para reemplazar los datos
        if st.button("Reemplazar datos en la base de datos"):
            reemplazar_datos_sqlite(df_nuevo)
    except Exception as e:
        st.error("Error al procesar el archivo subido.")
        st.error(str(e))

# Opción para descargar los datos de la base de datos
st.header("Descargar los datos de la base de datos")
df_actual = leer_datos_sqlite()

if not df_actual.empty:
    try:
        # Botón para descargar los datos como CSV
        st.download_button(
            label="Descargar datos como CSV",
            data=df_actual.to_csv(index=False),
            file_name="registro_correccion.csv",
            mime="text/csv"
        )
    except Exception as e:
        st.error("Error al preparar los datos para descargar.")
        st.error(str(e))
else:
    st.warning("No hay datos disponibles en la base de datos.")

