import streamlit as st
import pandas as pd
import os


# Solicitar contraseña al inicio
PASSWORD = "Tt5plco5"
input_password = st.text_input("Ingresa la contraseña para acceder:", type="password")

# Verificar la contraseña
if input_password != PASSWORD:
    st.error("Escribe la contraseña correcta, y presiona ENTER.")

    st.stop()



# Nombres de los archivos y sus respectivos encabezados
ARCHIVOS = {
    "registro_convocatorias.csv": "Área: Convocatorias",
    "registro_analisis.csv": "Área: Análisis Estadístico",
    "registro_protocolos.csv": "Área: Protocolos",
    "registro_correccion.csv": "Área: Corrección de Estilo"
}

def contar_registros_estados(archivo):
    try:
        # Leer el archivo CSV
        df = pd.read_csv(archivo)
        # Total de registros
        total_registros = len(df)
        # Registros con "Activo" en alguna columna
        registros_activos = int(df.apply(lambda x: x.astype(str).str.contains("Activo").any(), axis=1).sum())
        # Registros con "Terminado" en alguna columna
        registros_terminados = int(df.apply(lambda x: x.astype(str).str.contains("Terminado").any(), axis=1).sum())
        return total_registros, registros_activos, registros_terminados
    except Exception as e:
        st.error(f"Error al procesar {archivo}: {e}")
        return 0, 0, 0

# Título del programa
st.title("OASIS <Productividad>")

# Mostrar resultados para cada archivo
for archivo, encabezado in ARCHIVOS.items():
    if os.path.exists(archivo):
        st.subheader(encabezado)  # Mostrar el encabezado según el archivo
        total, activos, terminados = contar_registros_estados(archivo)
        st.write(f"Activos: {activos}")
        st.write(f"Terminados: {terminados}")
        st.write(f"Total registros: {total}")
    else:
        st.warning(f"El archivo {archivo} no se encuentra en la carpeta.")

# Nota para los usuarios
st.info("Revisión exitosa. Cierre la aplicación.")

