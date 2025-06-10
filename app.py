import streamlit as st
import pandas as pd
import requests
import xgboost as xgb
from predicciones import load_models, predict_fertility_and_cultivo  # Asegúrate de tener esta función implementada en tu archivo predicciones.py
from clima_api import get_weather_data  # Asegúrate de tener esta función implementada en tu archivo clima_api.py

# Función para obtener la altitud (elevación) usando Open-Elevation API
def get_elevation(lat, lon):
    url = f"https://api.open-elevation.com/api/v1/lookup?locations={lat},{lon}"
    response = requests.get(url)
    data = response.json()
    return data['results'][0]['elevation']  # Retorna la altitud en metros

# Función principal para la interfaz
def main():
    st.title("Predicción de Fertilidad del Suelo con Geolocalización")
    st.markdown("""
        <style>
            .main { 
                background-color: #f0f4f8; 
                padding: 20px; 
                border-radius: 10px;
            }
            h1 {
                color: #2C3E50;
            }
            .section-title {
                font-size: 1.5em;
                color: #3498DB;
            }
            .info-box {
                padding: 10px;
                border-radius: 5px;
                background-color: #ecf0f1;
            }
            .input-field {
                background-color: #d5dbdb;
            }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<div class='main'>", unsafe_allow_html=True)

    # Selección de cómo obtener los datos climáticos
    st.markdown("<div class='section-title'>Seleccione cómo desea obtener los datos climáticos</div>", unsafe_allow_html=True)
    weather_option = st.radio("¿Cómo deseas obtener los datos del clima?", 
                              ["Por coordenadas", "Por ubicación actual", "Manualmente"], key="weather_option")

    if weather_option == "Por coordenadas":
        col1, col2 = st.columns(2)
        with col1:
            lat = st.number_input("Latitud", value=0.0)
        with col2:
            lon = st.number_input("Longitud", value=0.0)

        if st.button("Obtener clima", key="get_weather_button"):
            # Obtener los datos climáticos
            weather_data = get_weather_data(lat, lon)
            
            # Verificar si la respuesta tiene los datos esperados (Temperatura y Humedad)
            if 'temperature' in weather_data and 'humidity' in weather_data:
                st.markdown(f"<div class='info-box'>Datos del clima: Temperatura: {weather_data['temperature']}°C, "
                            f"Humedad: {weather_data['humidity']}%</div>", unsafe_allow_html=True)
            else:
                st.error("Error: No se pudieron obtener los datos climáticos. Verifique la respuesta de la API.")
            
            # Obtener la altitud
            elevation = get_elevation(lat, lon)
            st.markdown(f"<div class='info-box'>Altitud: {elevation} metros</div>", unsafe_allow_html=True)

    elif weather_option == "Por ubicación actual":
        # Obtener ubicación actual del usuario
        st.write("Haz clic en el botón para obtener tu ubicación actual.")
        if st.button("Obtener ubicación actual"):
            location = st.text_input("Ubicación actual", value="No disponible")
            st.write(f"Ubicación: {location}")  # Aquí agregarías código para obtener la ubicación real.
            
            # Verificar si la respuesta tiene los datos esperados
            if 'temperature' in weather_data and 'humidity' in weather_data:
                st.markdown(f"<div class='info-box'>Datos del clima: Temperatura: {weather_data['temperature']}°C, "
                            f"Humedad: {weather_data['humidity']}%</div>", unsafe_allow_html=True)
            else:
                st.error("Error: No se pudieron obtener los datos climáticos. Verifique la respuesta de la API.")
            
            # Obtener la altitud
            elevation = get_elevation(lat, lon)
            st.markdown(f"<div class='info-box'>Altitud: {elevation} metros</div>", unsafe_allow_html=True)

    elif weather_option == "Manualmente":
        # Campos manuales
        humedad_suelo = st.number_input("Humedad (%)", min_value=0, max_value=100)

    # Entradas de datos del suelo
    st.markdown("<div class='section-title'>Datos del suelo</div>", unsafe_allow_html=True)
    tipo_suelo = st.selectbox("Tipo de suelo", [1, 2, 3, 4], key="tipo_suelo")
    pH = st.number_input("pH del suelo", min_value=0.0, max_value=14.0, key="ph")
    materia_organica = st.number_input("Materia orgánica (%)", min_value=0.0, max_value=100.0)
    conductividad = st.number_input("Conductividad (mS/cm)", min_value=0.0)
    nitrogeno = st.number_input("Nitrógeno (%)", min_value=0.0)
    fosforo = st.number_input("Fósforo (mg/kg)", min_value=0)
    potasio = st.number_input("Potasio (mg/kg)", min_value=0)
    densidad = st.number_input("Densidad (g/cm³)", min_value=0.0)
    altitud = st.number_input("Altitud (metros)", min_value=0)

    # Recoger la variable `humedad_suelo` que es la que ahora se usa
    humedad_suelo = st.number_input("Humedad del suelo (%)", min_value=0, max_value=100)

    # Cargar los modelos
    fertilidad_model, cultivo_model = load_models()

    # Predicción
    if st.button("Predecir", key="predict_button"):
        # Asegurarse de que el orden de las columnas sea correcto
        input_data = pd.DataFrame([[
            tipo_suelo, pH, materia_organica, conductividad, nitrogeno, fosforo, 
            potasio, humedad_suelo, densidad, altitud,
        ]], columns=[
            "tipo_suelo", "pH", "materia_organica", "conductividad", "nitrogeno", 
            "fosforo", "potasio", "humedad_suelo", "densidad", "altitud", 
        ])

        # Hacer la predicción con los modelos cargados
        fertility_prediction, crop_prediction = predict_fertility_and_cultivo(input_data, fertilidad_model, cultivo_model)

        # Mostrar las predicciones
        st.markdown(f"<div class='info-box'>Fertilidad Predicha: {fertility_prediction[0]}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='info-box'>Cultivo Predicho: {crop_prediction[0]}</div>", unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()









