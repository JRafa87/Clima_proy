import streamlit as st
import joblib
import numpy as np
import xgboost as xgb
import requests
from geopy.geocoders import Nominatim


# Función para cargar los modelos
def load_models():
    try:
        # Cargar los modelos desde las rutas proporcionadas
        fertilidad_model = joblib.load("fertilidad_model.json")  # Asegúrate de colocar la ruta correcta
        cultivo_model = joblib.load("cultivo_model.json")  # Asegúrate de colocar la ruta correcta
        return fertilidad_model, cultivo_model
    except FileNotFoundError as e:
        print(f"Error: No se pudo encontrar uno de los archivos de modelo. {str(e)}")
        return None, None
    except Exception as e:
        print(f"Error al cargar los modelos: {str(e)}")
        return None, None


# Función para predecir fertilidad y cultivo
def predict_fertility_and_cultivo(input_data, fertilidad_model, cultivo_model):
    # Verificar si los modelos se cargaron correctamente
    if fertilidad_model is None or cultivo_model is None:
        raise ValueError("Los modelos no se cargaron correctamente. Verifica los archivos.")
    
    try:
        # Convertir input_data a un formato adecuado para XGBoost (DMatrix o np.array)
        input_array = np.array(input_data).reshape(1, -1)  # Asegurarse de que sea un array 2D (una muestra)
        input_dmatrix = xgb.DMatrix(input_array)

        # Predicción de fertilidad
        fertilidad = int(fertilidad_model.predict(input_dmatrix)[0])  # Asegúrate de que el índice es correcto
        predicted_fertilidad = "Fértil" if fertilidad == 1 else "Infértil"
        
        # Predicción del cultivo basado en la fertilidad
        predicted_cultivo = "Ninguno"
        if fertilidad == 1:
            cultivo = int(cultivo_model.predict(input_dmatrix)[0])
            # Lista de cultivos posibles, en función del modelo de cultivo
            cultivos = [
                "Trigo", "Maíz", "Caña de Azúcar", "Algodón", "Arroz", "Papa",
                "Cebolla", "Tomate", "Batata", "Brócoli", "Café"
            ]
            predicted_cultivo = cultivos[cultivo] if cultivo < len(cultivos) else "Desconocido"
        
        return predicted_fertilidad, predicted_cultivo
    except Exception as e:
        print(f"Error en la predicción: {str(e)}")
        return "Error en la predicción", "Error en la predicción"


# Función para obtener los datos climáticos y la ubicación
def get_weather_data(lat, lon):
    api_key = "f75c529787e26621bbd744dd67c056b0"  # Reemplaza con tu propia API Key de OpenWeather
    base_url = "https://api.openweathermap.org/data/2.5/weather"
    
    params = {
        "lat": lat,
        "lon": lon,
        "appid": api_key,
        "units": "metric",
        "lang": "es"
    }

    try:
        response = requests.get(base_url, params=params)
        data = response.json()
        if response.status_code == 200:
            return data['main']['humidity']  # Solo retornar la humedad
        else:
            return {'error': f"Error: {data['message']}"}
    except Exception as e:
        return {'error': f"Error al obtener los datos: {str(e)}"}


def main():
    st.title("Predicción de Fertilidad del Suelo con Geolocalización")
    st.markdown("""<style> /* estilos aquí */ </style>""", unsafe_allow_html=True)

    st.markdown("<div class='main'>", unsafe_allow_html=True)

    # Selección de cómo obtener los datos climáticos
    st.markdown("<div class='section-title'>Seleccione cómo desea obtener los datos climáticos</div>", unsafe_allow_html=True)
    weather_option = st.radio("¿Cómo deseas obtener los datos del clima?", 
                              ["Por coordenadas", "Por ubicación actual", "Manualmente"], key="weather_option")

    # Variables para humedad y altitud
    humidity = 0.0
    elevation = 0.0
    location_name = None
    lat, lon = None, None

    if weather_option == "Por coordenadas":
        col1, col2 = st.columns(2)
        with col1:
            lat = st.number_input("Latitud", value=0.0)
        with col2:
            lon = st.number_input("Longitud", value=0.0)

        if st.button("Obtener clima", key="get_weather_button"):
            humidity = get_weather_data(lat, lon)
            if isinstance(humidity, int):  # Verificar que la humedad sea correcta
                st.markdown(f"Humedad: {humidity}%")
            else:
                st.error(f"Error: {humidity['error']}")

            # Obtener altitud (simulación)
            elevation = 1000  # Por ejemplo
            st.markdown(f"Altitud: {elevation} metros")
            location_name = "Ubicación desconocida"  # Reemplazar por la ubicación real si es necesario

    elif weather_option == "Por ubicación actual":
        st.write("Haz clic en el botón para obtener tu ubicación actual.")
        if st.button("Obtener ubicación actual"):
            lat, lon = 19.432608, -99.133209  # Ejemplo: Ciudad de México
            location_name = "Ciudad de México"
            st.write(f"Ubicación: {location_name}")
            humidity = get_weather_data(lat, lon)
            if isinstance(humidity, int):
                st.markdown(f"Humedad: {humidity}%")
            else:
                st.error(f"Error: {humidity['error']}")
            elevation = 1000  # Simulación
            st.markdown(f"Altitud: {elevation} metros")

    elif weather_option == "Manualmente":
        humedad = st.number_input("Humedad (%)", min_value=0, max_value=100)

    # Entradas de datos del suelo
    tipo_suelo = st.selectbox("Tipo de suelo", [1, 2, 3, 4], key="tipo_suelo")
    pH = st.number_input("pH del suelo", min_value=0.0, max_value=14.0, key="ph")
    materia_organica = st.number_input("Materia orgánica (%)", min_value=0.0, max_value=100.0)
    conductividad = st.number_input("Conductividad (mS/cm)", min_value=0.0)
    nitrogeno = st.number_input("Nitrógeno (%)", min_value=0.0)
    fosforo = st.number_input("Fósforo (mg/kg)", min_value=0)
    potasio = st.number_input("Potasio (mg/kg)", min_value=0)
    densidad = st.number_input("Densidad (g/cm³)", min_value=0.0)
    altitud = st.number_input("Altitud (metros)", value=elevation, min_value=0.0)
    humedad = st.number_input("Humedad (%)", value=humidity, min_value=0.0, max_value=100.0)

    # Realizar la predicción
    if st.button("Realizar predicción"):
        # Cargar los modelos
        fertilidad_model, cultivo_model = load_models()
        if fertilidad_model and cultivo_model:
            # Prepara los datos para la predicción
            input_data = [
                tipo_suelo, pH, materia_organica, conductividad, nitrogeno, fosforo, potasio, densidad, humedad, altitud
            ]
            # Realizar la predicción
            pred_fertilidad, pred_cultivo = predict_fertility_and_cultivo(input_data, fertilidad_model, cultivo_model)
            st.write(f"Predicción de Fertilidad: {pred_fertilidad}")
            st.write(f"Predicción de Cultivo: {pred_cultivo}")
        else:
            st.error("No se pudieron cargar los modelos de predicción.")

    # Botón para borrar datos
    if st.button("Borrar todos los datos"):
        st.session_state.clear()

    st.markdown("</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()


















