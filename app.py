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
            lat = st.number_input("Latitud")
        with col2:
            lon = st.number_input("Longitud")
        
        if st.button("Obtener clima"):
            weather_data = get_weather_data(lat, lon)
            elevation = get_elevation(lat, lon)
            
            if "error" not in weather_data:
                temperature = weather_data['temperature']
                humidity = weather_data['humidity']
                wind_speed = weather_data['wind_speed']
                
                st.markdown(f"<div class='info-box'>Temperatura: {temperature}°C</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='info-box'>Humedad: {humidity}%</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='info-box'>Velocidad del viento: {wind_speed} m/s</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='info-box'>Altitud: {elevation} m</div>", unsafe_allow_html=True)
                
                # Preparar datos para la predicción
                input_data = {
                    'temperature': [temperature],
                    'humidity': [humidity],
                    'wind_speed': [wind_speed],
                    'elevation': [elevation]
                }
                input_data_df = pd.DataFrame(input_data)
                
                # Cargar modelos
                fertilidad_model, cultivo_model = load_models()
                
                # Realizar predicciones
                fertility_prediction, crop_prediction = predict_fertility_and_cultivo(input_data_df, fertilidad_model, cultivo_model)
                
                st.markdown(f"<div class='info-box'>Predicción de fertilidad: {fertility_prediction[0]}</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='info-box'>Predicción de cultivo: {crop_prediction[0]}</div>", unsafe_allow_html=True)
            else:
                st.error(weather_data['error'])
    
    elif weather_option == "Por ubicación actual":
        # Aquí puedes agregar lógica para obtener la ubicación actual del usuario
        st.write("Funcionalidad no implementada aún.")
    
    elif weather_option == "Manualmente":
        # Aquí puedes agregar campos para que el usuario ingrese manualmente los datos climáticos
        st.write("Funcionalidad no implementada aún.")
    
    st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()




















