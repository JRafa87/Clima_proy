import streamlit as st
import requests
import pandas as pd
import xgboost as xgb
from clima_api import get_weather_data  # Asegúrate de tener esta función implementada en tu archivo clima_api.py

# Función para obtener la altitud (elevación) usando Open-Elevation API
def get_elevation(lat, lon):
    url = f"https://api.open-elevation.com/api/v1/lookup?locations={lat},{lon}"
    response = requests.get(url)
    data = response.json()
    return data['results'][0]['elevation']  # Retorna la altitud en metros

def load_models():
    # Cargar el modelo de fertilidad (en formato JSON)
    fertilidad_model = xgb.Booster()
    fertilidad_model.load_model('fertilidad_model.json')  # Asumiendo que el modelo fue guardado en .json

    # Cargar el modelo de cultivo (en formato JSON)
    cultivo_model = xgb.Booster()
    cultivo_model.load_model('cultivo_model.json')  # Lo mismo aquí

    return fertilidad_model, cultivo_model

def predict_fertility_and_cultivo(input_data, fertilidad_model, cultivo_model):
    # Convertir el dataframe de entrada a DMatrix, formato requerido por XGBoost
    input_dmatrix = xgb.DMatrix(input_data)

    # Predicciones con el modelo de fertilidad
    fertility_prediction = fertilidad_model.predict(input_dmatrix)

    # Predicciones con el modelo de cultivo
    crop_prediction = cultivo_model.predict(input_dmatrix)

    return fertility_prediction, crop_prediction

def get_weather_data(lat, lon):
    try:
        # Realiza la solicitud a la API para obtener los datos del clima
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid=YOUR_API_KEY"
        response = requests.get(url)
        data = response.json()

        if response.status_code == 200:
            # Extraer los datos relevantes de la respuesta
            temperature = data['main']['temp']
            humidity = data['main']['humidity']
            wind_speed = data['wind']['speed']

            return {
                'temperature': temperature,
                'humidity': humidity,
                'wind_speed': wind_speed
            }
        else:
            raise ValueError(f"Error en la API: {data.get('message', 'Sin detalles disponibles')}")
    except Exception as e:
        return {'error': str(e)}

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
            
            # Verificar si la respuesta tiene los datos esperados
            if 'temperature' in weather_data and 'humidity' in weather_data and 'wind_speed' in weather_data:
                st.markdown(f"<div class='info-box'>Datos del clima: Temperatura: {weather_data['temperature']}°C, "
                            f"Humedad: {weather_data['humidity']}%, Viento: {weather_data['wind_speed']} m/s</div>", unsafe_allow_html=True)
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
            
            # Simulamos una ubicación para este ejemplo:
            #lat, lon = 20.0, 0.0  # Estos valores deberían ser obtenidos de la geolocalización real.
            #weather_data = get_weather_data(lat, lon)
            
            # Verificar si la respuesta tiene los datos esperados
            if 'temperature' in weather_data and 'humidity' in weather_data and 'wind_speed' in weather_data:
                st.markdown(f"<div class='info-box'>Datos del clima: Temperatura: {weather_data['temperature']}°C, "
                            f"Humedad: {weather_data['humidity']}%, Viento: {weather_data['wind_speed']} m/s</div>", unsafe_allow_html=True)
            else:
                st.error("Error: No se pudieron obtener los datos climáticos. Verifique la respuesta de la API.")
            
            # Obtener la altitud
            elevation = get_elevation(lat, lon)
            st.markdown(f"<div class='info-box'>Altitud: {elevation} metros</div>", unsafe_allow_html=True)

    elif weather_option == "Manualmente":
        # Campos manuales
        temperature = st.number_input("Temperatura (°C)", min_value=-50, max_value=50)
        humidity = st.number_input("Humedad (%)", min_value=0, max_value=100)
        wind_speed = st.number_input("Velocidad del viento (m/s)", min_value=0.0)

    # Entradas de datos del suelo
    st.markdown("<div class='section-title'>Datos del suelo</div>", unsafe_allow_html=True)
    tipo_suelo = st.selectbox("Tipo de suelo", [1, 2, 3, 4], key="tipo_suelo")
    pH = st.number_input("pH del suelo", min_value=0.0, max_value=14.0, key="ph")
    materia_organica = st.number_input("Materia orgánica (%)", min_value=0.0, max_value=100.0)
    conductividad = st.number_input("Conductividad (mS/cm)", min_value=0.0)
    nitrogeno = st.number_input("Nitrógeno (%)", min_value=0.0)
    fosforo = st.number_input("Fósforo (mg/kg)", min_value=0)
    potasio = st.number_input("Potasio (mg/kg)", min_value=0)
    humedad_suelo = st.number_input("Humedad del suelo (%)", min_value=0, max_value=100)
    densidad = st.number_input("Densidad (g/cm³)", min_value=0.0)
    altitud = st.number_input("Altitud (metros)", min_value=0)

    # Recoger las variables del clima si están disponibles
    temperature = st.number_input("Temperatura (°C)", min_value=-50, max_value=50)
    humidity = st.number_input("Humedad (%)", min_value=0, max_value=100)
    wind_speed = st.number_input("Velocidad del viento (m/s)", min_value=0.0)

    # Cargar los modelos
    fertilidad_model, cultivo_model = load_models()

    # Predicción
    if st.button("Predecir", key="predict_button"):
        # Compilación de los datos para la predicción
        input_data = pd.DataFrame([[tipo_suelo, pH, materia_organica, conductividad, nitrogeno, fosforo, potasio, humedad_suelo, densidad, altitud, temperature, humidity, wind_speed]], 
                                  columns=["tipo_suelo", "pH", "materia_organica", "conductividad", "nitrogeno", "fosforo", "potasio", "humedad_suelo", "densidad", "altitud", "temperature", "humidity", "wind_speed"])

        # Hacer la predicción con los modelos cargados
        fertility_prediction, crop_prediction = predict_fertility_and_cultivo(input_data, fertilidad_model, cultivo_model)

        # Mostrar las predicciones
        st.markdown(f"<div class='info-box'>Fertilidad Predicha: {fertility_prediction[0]}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='info-box'>Cultivo Predicho: {crop_prediction[0]}</div>", unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()






