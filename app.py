import streamlit as st
import pandas as pd
from clima_api import get_weather_data  # Función para consultar el clima

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

    # Inicializar las variables de clima con un valor por defecto
    temperature = None
    humidity = None
    wind_speed = None

    # Obtener ubicación actual del usuario
    if weather_option == "Por ubicación actual":
        # Pedir permiso para geolocalización
        st.write("Por favor, permite el acceso a tu geolocalización para obtener tu ubicación y el clima.")
        get_user_location()

        # Aquí esperaríamos obtener los datos de la ubicación
        location_data = st.session_state.get('user_location', None)

        if location_data:
            lat = location_data['lat']
            lon = location_data['lon']
            st.write(f"Ubicación seleccionada: Latitud {lat}, Longitud {lon}")
            
            # Obtener los datos del clima con la ubicación seleccionada
            weather_data = get_weather_data(lat, lon)
            
            # Ahora procesamos los datos para extraer la información relevante
            try:
                # Asumimos que weather_data es un string, vamos a parsearlo como JSON o texto
                weather_data_dict = parse_weather_data(weather_data)
                temperature = weather_data_dict.get('temperature', None)
                humidity = weather_data_dict.get('humidity', None)
                wind_speed = weather_data_dict.get('wind_speed', None)

                # Guardar los datos climáticos en session_state
                st.session_state['temperature'] = temperature
                st.session_state['humidity'] = humidity
                st.session_state['wind_speed'] = wind_speed

                st.markdown(f"<div class='info-box'>Datos del clima: {weather_data_dict}</div>", unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Error al procesar los datos del clima: {e}")

    elif weather_option == "Por coordenadas":
        col1, col2 = st.columns(2)
        with col1:
            lat = st.number_input("Latitud", value=0.0)
        with col2:
            lon = st.number_input("Longitud", value=0.0)

        if st.button("Obtener clima", key="get_weather_button"):
            weather_data = get_weather_data(lat, lon)
            
            # Procesamos el resultado del clima
            try:
                weather_data_dict = parse_weather_data(weather_data)
                temperature = weather_data_dict.get('temperature', None)
                humidity = weather_data_dict.get('humidity', None)
                wind_speed = weather_data_dict.get('wind_speed', None)

                # Guardar los datos climáticos en session_state
                st.session_state['temperature'] = temperature
                st.session_state['humidity'] = humidity
                st.session_state['wind_speed'] = wind_speed

                st.markdown(f"<div class='info-box'>Datos del clima: {weather_data_dict}</div>", unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Error al procesar los datos del clima: {e}")

    elif weather_option == "Manualmente":
        st.markdown("<div class='section-title'>Ingrese los datos climáticos manualmente</div>", unsafe_allow_html=True)
        temperature = st.number_input("Temperatura (°C)", min_value=-50, max_value=50, key="temp")
        humidity = st.number_input("Humedad (%)", min_value=0, max_value=100, key="humidity")
        wind_speed = st.number_input("Velocidad del viento (m/s)", min_value=0.0, key="wind_speed")

        # Guardar los datos manuales en session_state
        st.session_state['temperature'] = temperature
        st.session_state['humidity'] = humidity
        st.session_state['wind_speed'] = wind_speed

    # Entradas de datos de suelo
    st.markdown("<div class='section-title'>Datos del suelo</div>", unsafe_allow_html=True)
    tipo_suelo = st.selectbox("Tipo de suelo", [1, 2, 3, 4], key="tipo_suelo")
    pH = st.number_input("pH del suelo", min_value=0.0, max_value=14.0, key="ph")

    # Asegurarse de que las variables climáticas no sean None antes de la predicción
    if 'temperature' in st.session_state and 'humidity' in st.session_state and 'wind_speed' in st.session_state:
        if st.button("Predecir", key="predict_button"):
            # Recuperar los datos del clima desde session_state
            temperature = st.session_state['temperature']
            humidity = st.session_state['humidity']
            wind_speed = st.session_state['wind_speed']

            # Compilación de los datos para la predicción
            input_data = pd.DataFrame([[tipo_suelo, pH, temperature, humidity, wind_speed]], 
                                      columns=["tipo_suelo", "pH", "temperature", "humidity", "wind_speed"])
            prediction = predict_fertility_and_cultivo(input_data)

            # Mostrar las predicciones
            st.markdown("<div class='info-box'>Fertilidad Predicha: {}</div>".format(prediction[0]), unsafe_allow_html=True)
            st.markdown("<div class='info-box'>Cultivo Predicho: {}</div>".format(prediction[1]), unsafe_allow_html=True)
    else:
        st.warning("Por favor, asegúrate de tener los datos climáticos completos antes de predecir.")

    st.markdown('</div>', unsafe_allow_html=True)

# Función para parsear los datos del clima (esto debe ser ajustado según el formato real)
def parse_weather_data(weather_data):
    # Supongo que weather_data es un string en formato de texto. 
    # Si es JSON o algo diferente, ajusta esta función.
    weather_dict = {}
    
    # Ejemplo de parsing si weather_data es un string como "Temperatura: 21.61°C, Humedad: 76%, Viento: 6.17 m/s"
    try:
        parts = weather_data.split(',')
        for part in parts:
            if 'Temperatura' in part:
                weather_dict['temperature'] = float(part.split(':')[1].replace('°C', '').strip())
            elif 'Humedad' in part:
                weather_dict['humidity'] = int(part.split(':')[1].replace('%', '').strip())
            elif 'Viento' in part:
                weather_dict['wind_speed'] = float(part.split(':')[1].replace('m/s', '').strip())
    except Exception as e:
        raise ValueError(f"Error al parsear los datos del clima: {e}")
    
    return weather_dict

# Predicción usando los modelos entrenados (esto se debe ajustar a tus modelos)
def predict_fertility_and_cultivo(input_data):
    # Aquí iría el código de tus modelos entrenados, por ejemplo:
    return ("Fértil", "Trigo")  # Simulación de resultados

if __name__ == "__main__":
    main()




