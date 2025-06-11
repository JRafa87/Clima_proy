import streamlit as st
import pandas as pd
import requests
from geopy.geocoders import Nominatim  # Importamos geopy
from predicciones import load_models, predict_fertility_and_cultivo

# Función para obtener el nombre del lugar a partir de latitud y longitud
def get_location_name(lat, lon):
    geolocator = Nominatim(user_agent="myGeocoder")
    location = geolocator.reverse((lat, lon), language='es', timeout=10)
    
    if location:
        return location.address  # Retorna la dirección completa (nombre del lugar)
    else:
        return "Ubicación desconocida"  # Si no se puede obtener el nombre

# Función para obtener los datos del clima
def get_weather_data(lat, lon):
    api_key = "f75c529787e26621bbd744dd67c056b0"  # Reemplaza con tu propia API Key de OpenWeather
    base_url = "https://api.openweathermap.org/data/2.5/weather"
    
    # Parámetros para la consulta
    params = {
        "lat": lat,
        "lon": lon,
        "appid": api_key,
        "units": "metric",  # Para obtener la temperatura en grados Celsius
        "lang": "es"  # Respuesta en español
    }
    
    try:
        # Hacer la solicitud GET
        response = requests.get(base_url, params=params)
        data = response.json()
        
        # Verificar si la respuesta es exitosa
        if response.status_code == 200:
            # Extraer la humedad
            humidity = data['main']['humidity']
            return humidity  # Retornar solo la humedad
        else:
            return {'error': f"Error en la solicitud: {data['message']}"}
    except Exception as e:
        return {'error': f"Error al obtener los datos: {str(e)}"}

# Función para obtener la altitud (elevación) usando Open-Elevation API
def get_elevation(lat, lon):
    url = f"https://api.open-elevation.com/api/v1/lookup?locations={lat},{lon}"
    response = requests.get(url)
    data = response.json()
    return data['results'][0]['elevation']  # Retorna la altitud en metros

# Función para asegurarse de que los valores sean numéricos
def get_numeric_value(value, default=0):
    return value if isinstance(value, (int, float)) else default

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

    # Variables para humedad y altitud
    humidity = 0  # Aseguramos que la humedad tenga un valor por defecto numérico
    elevation = 0  # Aseguramos que la altitud tenga un valor por defecto numérico
    location_name = None
    lat, lon = None, None

    if weather_option == "Por coordenadas":
        col1, col2 = st.columns(2)
        with col1:
            lat = st.number_input("Latitud", value=0.0)
        with col2:
            lon = st.number_input("Longitud", value=0.0)

        if st.button("Obtener clima", key="get_weather_button"):
            # Obtener los datos climáticos
            humidity = get_weather_data(lat, lon)  # Solo obtenemos la humedad

            # Verificar si la humedad fue obtenida correctamente
            if isinstance(humidity, int):  # Si la humedad es un valor entero, es correcta
                st.markdown(f"<div class='info-box'>Humedad: {humidity}%</div>", unsafe_allow_html=True)
            else:
                st.error(f"Error: {humidity['error']}")  # Mostramos el error si no fue posible obtener la humedad

            # Obtener la altitud
            elevation = get_elevation(lat, lon)
            st.markdown(f"<div class='info-box'>Altitud: {elevation} metros</div>", unsafe_allow_html=True)  # Solo el valor numérico

            # Obtener el nombre del lugar (opcional)
            location_name = get_location_name(lat, lon)
            st.markdown(f"<div class='info-box'>Ubicación: {location_name}</div>", unsafe_allow_html=True)

    elif weather_option == "Por ubicación actual":
        st.write("Haz clic en el botón para obtener tu ubicación actual.")
        if st.button("Obtener ubicación actual"):
            # Simulación de latitud y longitud (esto se debe reemplazar por la API real)
            lat, lon = 19.432608, -99.133209  # Ejemplo de latitud y longitud de Ciudad de México
            location_name = "Ciudad de México"  # Ejemplo
            st.write(f"Ubicación: {location_name}")

            # Obtener la humedad y altitud para esta ubicación
            humidity = get_weather_data(lat, lon)
            if isinstance(humidity, int):
                st.markdown(f"<div class='info-box'>Humedad: {humidity}%</div>", unsafe_allow_html=True)
            else:
                st.error(f"Error: {humidity['error']}")

            elevation = get_elevation(lat, lon)
            st.markdown(f"<div class='info-box'>Altitud: {elevation} metros</div>", unsafe_allow_html=True)  # Solo el valor numérico

    elif weather_option == "Manualmente":
        # Si elige "Manualmente", no se usan los valores de humedad ni altitud obtenidos automáticamente.
        humedad = st.number_input("Humedad (%)", min_value=0, max_value=100)

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

    # Validación y ajuste de valores numéricos
    elevation_value = get_numeric_value(elevation, 0)  # Asegura que la altitud es un número
    humidity_value = get_numeric_value(humidity, 0)  # Asegura que la humedad es un número

    # Ahora pasamos los valores validados a number_input
    altitud = st.number_input("Altitud (metros)", value=elevation_value, min_value=0)
    humedad = st.number_input("Humedad (%)", value=humidity_value, min_value=0, max_value=100)

    # Cargar los modelos
    fertilidad_model, cultivo_model = load_models()

    # Predicción
    if st.button("Predecir", key="predict_button"):
        # Asegurarse de que el orden de las columnas sea correcto
        input_data = pd.DataFrame([[tipo_suelo, pH, materia_organica, conductividad, nitrogeno, fosforo, potasio, densidad, humedad, altitud]],
                                  columns=["tipo_suelo", "ph", "materia_organica", "conductividad", "nitrogeno", "fosforo", "potasio", "densidad", "humedad", "altitud"])
        fertility, predicted_cultivo = predict_fertility_and_cultivo(input_data, fertilidad_model, cultivo_model)
        st.write(f"Fertilidad del suelo: {fertility}")
        st.write(f"Cultivo recomendado: {predicted_cultivo}")

    st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()










