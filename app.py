import streamlit as st
import pandas as pd
import requests
from geopy.geocoders import Nominatim
from predicciones import load_models, predict_fertility_and_cultivo

# Función para obtener el nombre del lugar a partir de latitud y longitud
def get_location_name(lat, lon):
    geolocator = Nominatim(user_agent="myGeocoder")
    location = geolocator.reverse((lat, lon), language='es', timeout=10)
    
    if location:
        return location.address
    else:
        return "Ubicación desconocida"

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
        "lang": "es"
    }
    
    try:
        response = requests.get(base_url, params=params)
        data = response.json()
        
        if response.status_code == 200:
            return data['main']['humidity']
        else:
            return {'error': f"Error en la solicitud: {data['message']}"}
    except Exception as e:
        return {'error': f"Error al obtener los datos: {str(e)}"}

# Función para obtener la altitud (elevación) usando Open-Elevation API
def get_elevation(lat, lon):
    url = f"https://api.open-elevation.com/api/v1/lookup?locations={lat},{lon}"
    response = requests.get(url)
    data = response.json()
    return data['results'][0]['elevation']

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
    humidity = None
    elevation = None
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

            if isinstance(humidity, int):
                st.markdown(f"<div class='info-box'>Humedad: {humidity}%</div>", unsafe_allow_html=True)
            else:
                st.error(f"Error: {humidity['error']}")  # Mostrar mensaje de error si no fue posible obtener la humedad

            # Obtener la altitud
            elevation = get_elevation(lat, lon)
            st.markdown(f"<div class='info-box'>Altitud: {elevation} metros</div>", unsafe_allow_html=True)

            # Obtener el nombre del lugar (opcional)
            location_name = get_location_name(lat, lon)
            st.markdown(f"<div class='info-box'>Ubicación: {location_name}</div>", unsafe_allow_html=True)

    elif weather_option == "Por ubicación actual":
        st.write("Haz clic en el botón para obtener tu ubicación actual.")
        if st.button("Obtener ubicación actual"):
            lat, lon = 19.432608, -99.133209  # Ejemplo de latitud y longitud de Ciudad de México
            location_name = "Ciudad de México"
            st.write(f"Ubicación: {location_name}")

            # Obtener la humedad y altitud para esta ubicación
            humidity = get_weather_data(lat, lon)
            if isinstance(humidity, int):
                st.markdown(f"<div class='info-box'>Humedad: {humidity}%</div>", unsafe_allow_html=True)
            else:
                st.error(f"Error: {humidity['error']}")

            elevation = get_elevation(lat, lon)
            st.markdown(f"<div class='info-box'>Altitud: {elevation} metros</div>", unsafe_allow_html=True)

    elif weather_option == "Manualmente":
        humedad = st.number_input("Humedad (%)", min_value=0, max_value=100)

    # Datos del suelo
    st.markdown("<div class='section-title'>Datos del suelo</div>", unsafe_allow_html=True)
    tipo_suelo = st.selectbox("Tipo de suelo", [1, 2, 3, 4], key="tipo_suelo")
    pH = st.number_input("pH del suelo", min_value=0.0, max_value=14.0, key="ph")
    materia_organica = st.number_input("Materia orgánica (%)", min_value=0.0, max_value=100.0)
    conductividad = st.number_input("Conductividad (mS/cm)", min_value=0.0)
    nitrogeno = st.number_input("Nitrógeno (%)", min_value=0.0)
    fosforo = st.number_input("Fósforo (mg/kg)", min_value=0)
    potasio = st.number_input("Potasio (mg/kg)", min_value=0)
    densidad = st.number_input("Densidad (g/cm³)", min_value=0.0)

    # Validar y ajustar los valores
    def get_numeric_value(value, default=0):
        return value if isinstance(value, (int, float)) else default

    elevation_value = get_numeric_value(elevation, 0)
    humidity_value = get_numeric_value(humidity, 0)

    # Asegúrate de que los valores no desaparezcan al realizar la predicción
    altitud = st.number_input("Altitud (metros)", value=elevation_value, min_value=0)
    humedad = st.number_input("Humedad (%)", value=humidity_value, min_value=0, max_value=100)

    # Cargar los modelos
    fertilidad_model, cultivo_model = load_models()

    # Predicción
    if st.button("Predecir", key="predict_button"):
        if fertilidad_model and cultivo_model:
            # Asegúrate de que el orden de las columnas sea correcto
            input_data = pd.DataFrame([[tipo_suelo, pH, materia_organica, conductividad, nitrogeno, fosforo, potasio, densidad, humedad, altitud]],
                                      columns=["tipo_suelo", "ph", "materia_organica", "conductividad", "nitrogeno", "fosforo", "potasio", "densidad", "humedad", "altitud"])
            fertility, predicted_cultivo = predict_fertility_and_cultivo(input_data, fertilidad_model, cultivo_model)
            st.write(f"Fertilidad del suelo: {fertility}")
            st.write(f"Cultivo recomendado: {predicted_cultivo}")
        else:
            st.error("Los modelos no se han cargado correctamente. Verifica las rutas o archivos.")

    st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()








