import streamlit as st
import numpy as np
import xgboost as xgb
import requests
from streamlit.components.v1 import html

# -------------------- Cargar modelos -------------------- #
def load_models():
    try:
        fertilidad_model = xgb.Booster()
        fertilidad_model.load_model("fertilidad_model.json")

        cultivo_model = xgb.Booster()
        cultivo_model.load_model("cultivo_model.json")

        return fertilidad_model, cultivo_model
    except Exception as e:
        st.error(f"Error al cargar modelos: {e}")
        return None, None

# -------------------- Predicción -------------------- #
def predict_fertility_and_cultivo(input_data, fertilidad_model, cultivo_model):
    input_array = np.array(input_data).reshape(1, -1)
    input_dmatrix = xgb.DMatrix(input_array)

    fertilidad = int(fertilidad_model.predict(input_dmatrix)[0])
    pred_fertilidad = "Fértil" if fertilidad == 1 else "Infértil"

    if fertilidad == 1:
        cultivo = int(cultivo_model.predict(input_dmatrix)[0])
        cultivos = [
            "Trigo", "Maíz", "Caña de Azúcar", "Algodón", "Arroz", "Papa",
            "Cebolla", "Tomate", "Batata", "Brócoli", "Café"
        ]
        pred_cultivo = cultivos[cultivo] if cultivo < len(cultivos) else "Desconocido"
    else:
        pred_cultivo = "Ninguno"

    return pred_fertilidad, pred_cultivo

# -------------------- APIs -------------------- #
def get_weather_data(lat, lon):
    api_key = "f75c529787e26621bbd744dd67c056b0"
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"lat": lat, "lon": lon, "appid": api_key, "units": "metric"}
    try:
        response = requests.get(url, params=params).json()
        return response['main']['humidity']
    except:
        return None

def get_altitude(lat, lon):
    url = "https://api.open-elevation.com/api/v1/lookup"
    params = {"locations": f"{lat},{lon}"}
    try:
        response = requests.get(url, params=params).json()
        return response['results'][0]['elevation']
    except:
        return None

# -------------------- App Principal -------------------- #
def main():
    st.title("Predicción de Fertilidad del Suelo con Geolocalización")

    st.markdown("### Seleccione cómo desea obtener los datos climáticos")
    weather_option = st.radio("¿Cómo deseas obtener los datos del clima?",
                              ["Por coordenadas", "Por ubicación actual", "Manualmente"])

    humidity = 0.0
    elevation = 0.0
    lat, lon = None, None

    if weather_option == "Por coordenadas":
        lat = st.number_input("Latitud", format="%.6f")
        lon = st.number_input("Longitud", format="%.6f")
        if st.button("Obtener clima"):
            humidity = get_weather_data(lat, lon)
            elevation = get_altitude(lat, lon)
            st.write(f"Humedad: {humidity}%")
            st.write(f"Altitud: {elevation} m")

    elif weather_option == "Por ubicación actual":
        st.info("Haz clic abajo para permitir el acceso a tu ubicación.")
        location = st.empty()

        html_code = """
        <script>
        navigator.geolocation.getCurrentPosition(
            (pos) => {
                const coords = pos.coords;
                const latlon = `${coords.latitude},${coords.longitude}`;
                window.parent.postMessage({type: 'location', latlon: latlon}, "*");
            }
        );
        </script>
        """
        html(html_code)

        # Captura de coordenadas desde JS
        js_data = st.experimental_get_query_params()
        message = st.experimental_get_url_query_params()

        # Esperar el mensaje de JS
        from streamlit_javascript import st_javascript
        loc = st_javascript("""await new Promise((resolve) => {
            navigator.geolocation.getCurrentPosition((position) => {
                resolve(position.coords.latitude + "," + position.coords.longitude);
            });
        });""")

        if loc:
            try:
                lat, lon = map(float, loc.split(","))
                st.success(f"Ubicación obtenida: Latitud {lat}, Longitud {lon}")
                humidity = get_weather_data(lat, lon)
                elevation = get_altitude(lat, lon)
                st.write(f"Humedad: {humidity}%")
                st.write(f"Altitud: {elevation} m")
            except:
                st.error("Error al procesar la ubicación.")

    elif weather_option == "Manualmente":
        humidity = st.number_input("Humedad (%)", min_value=0.0, max_value=100.0)
        elevation = st.number_input("Altitud (m)", min_value=0.0)

    # Datos del suelo
    tipo_suelo = st.selectbox("Tipo de suelo", [1, 2, 3, 4])
    pH = st.number_input("pH del suelo", min_value=0.0, max_value=14.0)
    materia_organica = st.number_input("Materia orgánica (%)", min_value=0.0)
    conductividad = st.number_input("Conductividad (mS/cm)", min_value=0.0)
    nitrogeno = st.number_input("Nitrógeno (%)", min_value=0.0)
    fosforo = st.number_input("Fósforo (mg/kg)", min_value=0)
    potasio = st.number_input("Potasio (mg/kg)", min_value=0)
    densidad = st.number_input("Densidad (g/cm³)", min_value=0.0)

    if st.button("Realizar predicción"):
        fertilidad_model, cultivo_model = load_models()
        if fertilidad_model and cultivo_model and humidity is not None and elevation is not None:
            input_data = [
                tipo_suelo, pH, materia_organica, conductividad,
                nitrogeno, fosforo, potasio, densidad, humidity, elevation
            ]
            pred_fert, pred_cult = predict_fertility_and_cultivo(input_data, fertilidad_model, cultivo_model)
            st.success(f"Fertilidad: {pred_fert}")
            st.info(f"Cultivo recomendado: {pred_cult}")
        else:
            st.error("Faltan datos necesarios o no se cargaron los modelos.")

if __name__ == "__main__":
    main()



















