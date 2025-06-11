import streamlit as st
import requests
import pandas as pd
import xgboost as xgb

# Función para obtener la altitud
def get_elevation(lat, lon):
    url = f"https://api.open-elevation.com/api/v1/lookup?locations={lat},{lon}"
    response = requests.get(url)
    data = response.json()
    return data['results'][0]['elevation']

# ✅ Función para obtener datos del clima desde OpenWeatherMap
def get_weather_data(lat, lon):
    api_key = "f75c529787e26621bbd744dd67c056b0"  # Reemplaza con tu propia clave si es necesario
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "lat": lat,
        "lon": lon,
        "appid": api_key,
        "units": "metric"
    }
    try:
        response = requests.get(url, params=params)
        data = response.json()
        weather = {
            "temperature": data["main"]["temp"],
            "humidity": data["main"]["humidity"],
            "wind_speed": data["wind"]["speed"]
        }
        return weather
    except Exception as e:
        return {"error": str(e)}

# Cargar modelos
def load_models():
    fertilidad_model = xgb.Booster()
    fertilidad_model.load_model('fertilidad_model.json')

    cultivo_model = xgb.Booster()
    cultivo_model.load_model('cultivo_model.json')

    return fertilidad_model, cultivo_model

# Realizar predicciones
def predict_fertility_and_cultivo(input_data, fertilidad_model, cultivo_model):
    input_dmatrix = xgb.DMatrix(input_data)
    fertility_prediction = fertilidad_model.predict(input_dmatrix)
    crop_prediction = cultivo_model.predict(input_dmatrix)
    return fertility_prediction, crop_prediction

# App principal
def main():
    st.title("Predicción de Fertilidad del Suelo con Geolocalización")

    st.markdown("""<style>
        .main { background-color: #f0f4f8; padding: 20px; border-radius: 10px; }
        h1 { color: #2C3E50; }
        .section-title { font-size: 1.5em; color: #3498DB; }
        .info-box { padding: 10px; border-radius: 5px; background-color: #ecf0f1; }
    </style>""", unsafe_allow_html=True)

    st.markdown("<div class='main'>", unsafe_allow_html=True)

    # Selección de origen del clima
    st.markdown("<div class='section-title'>Seleccione cómo desea obtener los datos climáticos</div>", unsafe_allow_html=True)
    weather_option = st.radio("¿Cómo deseas obtener los datos del clima?",
                              ["Por coordenadas", "Por ubicación actual", "Manualmente"])

    if weather_option == "Por coordenadas":
        col1, col2 = st.columns(2)
        with col1:
            lat = st.number_input("Latitud", value=19.4326)
        with col2:
            lon = st.number_input("Longitud", value=-99.1332)

        if st.button("Obtener clima"):
            weather_data = get_weather_data(lat, lon)
            elevation = get_elevation(lat, lon)
            if "error" not in weather_data:
                st.markdown(f"<div class='info-box'>Temperatura: {weather_data['temperature']}°C, "
                            f"Humedad: {weather_data['humidity']}%, Viento: {weather_data['wind_speed']} m/s</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='info-box'>Altitud: {elevation} metros</div>", unsafe_allow_html=True)
            else:
                st.error("Error al obtener el clima: " + weather_data["error"])

    elif weather_option == "Por ubicación actual":
        st.write("Haz clic en el botón para obtener tu ubicación actual.")
        if st.button("Obtener ubicación actual"):
            # Aquí normalmente iría geolocalización por navegador, pero usaremos CDMX como valor por defecto
            lat, lon = 19.4326, -99.1332
            st.write("Ubicación: Ciudad de México")

            weather_data = get_weather_data(lat, lon)
            elevation = get_elevation(lat, lon)
            if "error" not in weather_data:
                st.markdown(f"<div class='info-box'>Temperatura: {weather_data['temperature']}°C, "
                            f"Humedad: {weather_data['humidity']}%, Viento: {weather_data['wind_speed']} m/s</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='info-box'>Altitud: {elevation} metros</div>", unsafe_allow_html=True)
            else:
                st.error("Error al obtener el clima: " + weather_data["error"])

    elif weather_option == "Manualmente":
        temperature = st.number_input("Temperatura (°C)", min_value=-50, max_value=50)
        humidity = st.number_input("Humedad (%)", min_value=0, max_value=100)
        wind_speed = st.number_input("Velocidad del viento (m/s)", min_value=0.0)
        elevation = st.number_input("Altitud (m)", min_value=0)

    # Entradas del suelo
    st.markdown("<div class='section-title'>Datos del suelo</div>", unsafe_allow_html=True)
    tipo_suelo = st.selectbox("Tipo de suelo", [1, 2, 3, 4])
    pH = st.number_input("pH del suelo", min_value=0.0, max_value=14.0)
    materia_organica = st.number_input("Materia orgánica (%)", min_value=0.0)
    conductividad = st.number_input("Conductividad (mS/cm)", min_value=0.0)
    nitrogeno = st.number_input("Nitrógeno (%)", min_value=0.0)
    fosforo = st.number_input("Fósforo (mg/kg)", min_value=0)
    potasio = st.number_input("Potasio (mg/kg)", min_value=0)
    humedad_suelo = st.number_input("Humedad del suelo (%)", min_value=0, max_value=100)
    densidad = st.number_input("Densidad (g/cm³)", min_value=0.0)

    # Definir variables climáticas según opción
    if weather_option == "Manualmente":
        pass  # Ya están definidas
    elif weather_option in ["Por coordenadas", "Por ubicación actual"]:
        # Reusar los valores obtenidos
        temperature = weather_data.get("temperature", 0)
        humidity = weather_data.get("humidity", 0)
        wind_speed = weather_data.get("wind_speed", 0)
    else:
        temperature = humidity = wind_speed = 0.0

    # Altitud (si se obtuvo)
    if weather_option != "Manualmente":
        altitud = elevation
    else:
        altitud = st.number_input("Altitud (m)", min_value=0)

    # Cargar modelos
    fertilidad_model, cultivo_model = load_models()

    # Botón de predicción
    if st.button("Predecir"):
        input_data = pd.DataFrame([[tipo_suelo, pH, materia_organica, conductividad, nitrogeno, fosforo,
                                    potasio, densidad, altitud, humidity]],
                                  columns=["tipo_suelo", "pH", "materia_organica", "conductividad",
                                           "nitrogeno", "fosforo", "potasio",
                                           "densidad", "altitud","humidity"])

        fertility_prediction, crop_prediction = predict_fertility_and_cultivo(input_data, fertilidad_model, cultivo_model)

        st.markdown(f"<div class='info-box'>Fertilidad Predicha: {fertility_prediction[0]:.2f}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='info-box'>Cultivo Predicho: {crop_prediction[0]:.2f}</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()




















