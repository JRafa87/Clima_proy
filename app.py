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
            # Devuelve un diccionario de error para que la función principal lo maneje
            return {'error': f"Error en la solicitud: {data['message']}"}
    except requests.exceptions.RequestException as e:
        # Captura errores de conexión o HTTP específicos de requests
        return {'error': f"Error de conexión al obtener el clima: {str(e)}"}
    except Exception as e:
        # Captura cualquier otro tipo de error
        return {'error': f"Error inesperado al obtener los datos del clima: {str(e)}"}

# Función para obtener la altitud (elevación) usando Open-Elevation API
def get_elevation(lat, lon):
    url = f"https://api.open-elevation.com/api/v1/lookup?locations={lat},{lon}"
    try:
        response = requests.get(url)
        response.raise_for_status() # Lanza una excepción para errores HTTP (4xx o 5xx)
        data = response.json()
        if data and 'results' in data and len(data['results']) > 0:
            return data['results'][0]['elevation']
        else:
            return None # O manejar como un error
    except requests.exceptions.RequestException as e:
        st.error(f"Error de conexión al obtener la altitud: {e}. Asegúrate de que la API de Open-Elevation esté accesible.")
        return None
    except Exception as e:
        st.error(f"Error inesperado al obtener la altitud: {e}")
        return None

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

    # Inicializar variables de estado para mantener los valores
    # **Aseguramos que siempre sean flotantes desde el inicio.**
    if 'humidity_display' not in st.session_state:
        st.session_state.humidity_display = 0.0
    if 'elevation_display' not in st.session_state:
        st.session_state.elevation_display = 0.0
    if 'location_name_display' not in st.session_state:
        st.session_state.location_name_display = "No obtenida"

    # Selección de cómo obtener los datos climáticos
    st.markdown("<div class='section-title'>Seleccione cómo desea obtener los datos climáticos</div>", unsafe_allow_html=True)
    weather_option = st.radio("¿Cómo deseas obtener los datos del clima?", 
                              ["Por coordenadas", "Por ubicación actual", "Manualmente"], key="weather_option")

    # Variables que se usarán en la predicción
    # Se inicializan con los valores de session_state (que ya son flotantes)
    humidity_for_prediction = st.session_state.humidity_display
    elevation_for_prediction = st.session_state.elevation_display
    
    # Esta variable se usa para mostrar el nombre de la ubicación
    location_name_for_display = st.session_state.location_name_display

    if weather_option == "Por coordenadas":
        col1, col2 = st.columns(2)
        with col1:
            lat = st.number_input("Latitud", value=0.0, format="%.6f", key="lat_coord")
        with col2:
            lon = st.number_input("Longitud", value=0.0, format="%.6f", key="lon_coord")

        if st.button("Obtener clima y altitud", key="get_weather_button_coords"):
            # Obtener los datos climáticos
            humidity_data = get_weather_data(lat, lon)
            if isinstance(humidity_data, int): # Solo si es un int (valor válido)
                st.session_state.humidity_display = float(humidity_data)
                st.markdown(f"<div class='info-box'>Humedad: {st.session_state.humidity_display}%</div>", unsafe_allow_html=True)
            else:
                st.error(f"Error al obtener humedad: {humidity_data.get('error', 'Error desconocido')}")
                st.session_state.humidity_display = 0.0 # Aseguramos que siga siendo numérico
                
            # Obtener la altitud
            elevation_data = get_elevation(lat, lon)
            if elevation_data is not None: # Solo si no es None (valor válido)
                st.session_state.elevation_display = float(elevation_data)
                st.markdown(f"<div class='info-box'>Altitud: {st.session_state.elevation_display} metros</div>", unsafe_allow_html=True)
            else:
                st.session_state.elevation_display = 0.0 # Aseguramos que siga siendo numérico

            # Obtener el nombre del lugar
            st.session_state.location_name_display = get_location_name(lat, lon)
            st.markdown(f"<div class='info-box'>Ubicación: {st.session_state.location_name_display}</div>", unsafe_allow_html=True)
            
            # Aseguramos que las variables para la predicción se actualicen AHORA
            humidity_for_prediction = st.session_state.humidity_display
            elevation_for_prediction = st.session_state.elevation_display


    elif weather_option == "Por ubicación actual":
        st.write("Haz clic en el botón para obtener tu ubicación actual (ejemplo de Ciudad de México).")
        if st.button("Obtener ubicación actual", key="get_current_location_button"):
            # Ejemplo de latitud y longitud de Ciudad de México
            lat, lon = 19.432608, -99.133209 
            
            # Obtener la humedad y altitud para esta ubicación
            humidity_data = get_weather_data(lat, lon)
            if isinstance(humidity_data, int):
                st.session_state.humidity_display = float(humidity_data)
                st.markdown(f"<div class='info-box'>Humedad: {st.session_state.humidity_display}%</div>", unsafe_allow_html=True)
            else:
                st.error(f"Error al obtener humedad: {humidity_data.get('error', 'Error desconocido')}")
                st.session_state.humidity_display = 0.0

            elevation_data = get_elevation(lat, lon)
            if elevation_data is not None:
                st.session_state.elevation_display = float(elevation_data)
                st.markdown(f"<div class='info-box'>Altitud: {st.session_state.elevation_display} metros</div>", unsafe_allow_html=True)
            else:
                st.session_state.elevation_display = 0.0

            st.session_state.location_name_display = get_location_name(lat, lon)
            st.markdown(f"<div class='info-box'>Ubicación: {st.session_state.location_name_display}</div>", unsafe_allow_html=True)

            # Aseguramos que las variables para la predicción se actualicen AHORA
            humidity_for_prediction = st.session_state.humidity_display
            elevation_for_prediction = st.session_state.elevation_display
    
    # Mostrar el nombre de la ubicación actual (persiste)
    st.markdown(f"<div class='info-box'>Última Ubicación Obtenida: {st.session_state.location_name_display}</div>", unsafe_allow_html=True)

    # Entradas de humedad y altitud que se muestran al usuario
    if weather_option == "Manualmente":
        # Permite al usuario introducir manualmente la humedad y altitud
        # Y actualiza directamente session_state y las variables para la predicción
        st.session_state.humidity_display = st.number_input("Humedad (%)", min_value=0, max_value=100, value=float(st.session_state.humidity_display), key="manual_hum")
        st.session_state.elevation_display = st.number_input("Altitud (metros)", min_value=0, value=float(st.session_state.elevation_display), key="manual_alt")
        humidity_for_prediction = st.session_state.humidity_display
        elevation_for_prediction = st.session_state.elevation_display
    else:
        # Para "Por coordenadas" y "Por ubicación actual", los campos están deshabilitados
        # y muestran los valores obtenidos de la API (guardados en session_state)
        # Es crucial asegurar que el 'value' es un flotante.
        st.number_input("Humedad (%)", min_value=0, max_value=100, value=float(st.session_state.humidity_display), disabled=True, key="display_hum")
        st.number_input("Altitud (metros)", min_value=0, value=float(st.session_state.elevation_display), disabled=True, key="display_alt")
        # Las variables humidity_for_prediction y elevation_for_prediction ya tienen los valores correctos de session_state
        # al inicio del main() para estas opciones, y se actualizan en el botón si se obtienen nuevos datos.


    # Datos del suelo
    st.markdown("<div class='section-title'>Datos del suelo</div>", unsafe_allow_html=True)
    tipo_suelo = st.selectbox("Tipo de suelo", [1, 2, 3, 4], key="tipo_suelo")
    pH = st.number_input("pH del suelo", min_value=0.0, max_value=14.0, format="%.2f", key="ph")
    materia_organica = st.number_input("Materia orgánica (%)", min_value=0.0, max_value=100.0, format="%.2f")
    conductividad = st.number_input("Conductividad (mS/cm)", min_value=0.0, format="%.2f")
    nitrogeno = st.number_input("Nitrógeno (%)", min_value=0.0, format="%.2f")
    fosforo = st.number_input("Fósforo (mg/kg)", min_value=0)
    potasio = st.number_input("Potasio (mg/kg)", min_value=0)
    densidad = st.number_input("Densidad (g/cm³)", min_value=0.0, format="%.2f")

    # Cargar los modelos
    try:
        fertilidad_model, cultivo_model = load_models()
    except Exception as e:
        st.error(f"Error al cargar los modelos: {e}. Asegúrate de que 'predicciones.py' y los archivos de modelo existen y son accesibles.")
        fertilidad_model, cultivo_model = None, None


    # Predicción
    if st.button("Predecir", key="predict_button"):
        if fertilidad_model and cultivo_model:
            # Asegúrate de que el orden de las columnas sea correcto
            input_data = pd.DataFrame([[tipo_suelo, pH, materia_organica, conductividad, nitrogeno, fosforo, potasio, densidad, humidity_for_prediction, elevation_for_prediction]],
                                      columns=["tipo_suelo", "ph", "materia_organica", "conductividad", "nitrogeno", "fosforo", "potasio", "densidad", "humedad", "altitud"])
            
            # Debugging: print input data before prediction
            st.write("Datos de entrada para la predicción:")
            st.write(input_data)

            fertility, predicted_cultivo = predict_fertility_and_cultivo(input_data, fertilidad_model, cultivo_model)
            st.success(f"Fertilidad del suelo: {fertility}")
            st.success(f"Cultivo recomendado: {predicted_cultivo}")
        else:
            st.error("Los modelos no se han cargado correctamente. Verifica las rutas o archivos.")

    st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()








