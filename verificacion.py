import os
import streamlit as st

archivo = "registro_convocatorias.csv"

# Obtener la ruta absoluta
archivo_path = os.path.abspath(archivo)
st.write("Ruta absoluta del archivo:", archivo_path)

# Verificar si el archivo existe
if os.path.exists(archivo_path):
    st.success(f"El archivo {archivo} existe.")
else:
    st.error(f"El archivo {archivo} no se encuentra en la ruta: {archivo_path}")

