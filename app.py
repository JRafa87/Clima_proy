import streamlit as st
import streamlit_folium as st_folium
from folium import Map, Marker
from clima_api import get_weather_data  # Función para consultar el clima
import pandas as pd

# Función principal para la interfaz
def main():
    # Título y estilos
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
            .button {
                background-color: #3498DB;
                color: white;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 16px;
            }
            .button:hover {
                background-color: #2980B9;
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
            weather_data = get_weather_data(lat, lon)
            st.markdown(f"<div class='info-box'>Datos del clima: {weather_data}</div>", unsafe_allow_html=True)

    elif weather_option == "Por ubicación actual":
        # Mapa interactivo para obtener ubicación
        st.markdown("<div class='section-title'>Seleccione su ubicación en el mapa</div>", unsafe_allow_html=True)
        st.write("Haz clic en el mapa para seleccionar tu ubicación")

        # Mostrar el mapa y permitir al usuario seleccionar la ubicación
        folium_map = Map(location=[20.0, 0.0], zoom_start=2)  # Mapa centrado en el mundo
        marker = Marker([20.0, 0.0])  # Marcador inicial en el mapa
        folium_map.add_child(marker)

        # Mostrar mapa en la app Streamlit
        map_response = st_folium(folium_map, width=700, height=500)

        # Verificar si se seleccionó una ubicación en el mapa
        if map_response and "lat" in map_response and "lon" in map_response:
            lat = map_response['lat']
            lon = map_response['lon']
            st.write(f"Ubicación seleccionada: Latitud {lat}, Longitud {lon}")

            # Obtener los datos del clima con la ubicación seleccionada
            weather_data = get_weather_data(lat, lon)
            st.markdown(f"<div class='info-box'>Datos del clima: {weather_data}</div>", unsafe_allow_html=True)

    elif weather_option == "Manualmente":
        st.markdown("<div class='section-title'>Ingrese los datos climáticos manualmente</div>", unsafe_allow_html=True)
        temperature = st.number_input("Temperatura (°C)", min_value=-50, max_value=50, key="temp")
        humidity = st.number_input("Humedad (%)", min_value=0, max_value=100, key="humidity")
        wind_speed = st.number_input("Velocidad del viento (m/s)", min_value=0.0, key="wind_speed")

    # Entradas de datos de suelo
    st.markdown("<div class='section-title'>Datos del suelo</div>", unsafe_allow_html=True)
    tipo_suelo = st.selectbox("Tipo de suelo", [1, 2, 3, 4], key="tipo_suelo")
    pH = st.number_input("pH del suelo", min_value=0.0, max_value=14.0, key="ph")

    if st.button("Predecir", key="predict_button"):
        # Compilación de los datos para la predicción
        input_data = pd.DataFrame([[tipo_suelo, pH, temperature, humidity, wind_speed]], 
                                  columns=["tipo_suelo", "pH", "temperature", "humidity", "wind_speed"])
        prediction = predict_fertility_and_cultivo(input_data)

        # Mostrar las predicciones
        st.markdown("<div class='info-box'>Fertilidad Predicha: {}</div>".format(prediction[0]), unsafe_allow_html=True)
        st.markdown("<div class='info-box'>Cultivo Predicho: {}</div>".format(prediction[1]), unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# Predicción usando los modelos entrenados (esto se debe ajustar a tus modelos)
def predict_fertility_and_cultivo(input_data):
    # Aquí iría el código de tus modelos entrenados, por ejemplo:
    # return (fertility_pred, crop_pred)
    return ("Fértil", "Trigo")  # Simulación de resultados

if __name__ == "__main__":
    main()
