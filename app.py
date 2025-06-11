import streamlit as st
import requests
import pandas as pd
import numpy as np
import xgboost as xgb

# Obtener ubicación aproximada desde la IP
def get_location_from_ip():
    try:
        res = requests.get("https://ipinfo.io/json")
        data = res.json()
        loc = data["loc"].split(",")
        city = data.get("city", "Ciudad desconocida")
        return float(loc[0]), float(loc[1]), city
    except:
        return None, None, "Ubicación no disponible"

# Altitud
def get_elevation(lat, lon):
    try:
        url = f"https://api.open-elevation.com/api/v1/lookup?locations={lat},{lon}"
        response = requests.get(url)
        data = response.json()
        return float(data['results'][0]['elevation'])
    except:
        return None

# Humedad (OpenWeatherMap)
def get_humidity(lat, lon):
    api_key = "f75c529787e26621bbd744dd67c056b0"
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"lat": lat, "lon": lon, "appid": api_key, "units": "metric"}
    try:
        response = requests.get(url, params=params)
        data = response.json()
        return float(data["main"]["humidity"])
    except:
        return None

# Cargar modelos
def load_models():
    fertilidad_model = xgb.Booster()
    cultivo_model = xgb.Booster()
    fertilidad_model.load_model("fertilidad_model.json")
    cultivo_model.load_model("cultivo_model.json")
    return fertilidad_model, cultivo_model

# Inicializar session_state
default_values = {
    'humedad': 0.0, 'altitud': 0.0, 'latitud': 0.0, 'longitud': 0.0, 'ubicacion': ''
}
for key, val in default_values.items():
    if key not in st.session_state:
        st.session_state[key] = val

# App principal
def main():
    st.title("🌾 Predicción de Fertilidad y Cultivo")

    metodo = st.radio("Método de ingreso de datos:", ["Por coordenadas", "Por ubicación actual", "Manual"])

    lat = lon = None

    if metodo == "Por coordenadas":
        col1, col2 = st.columns(2)
        with col1:
            lat = st.number_input("Latitud", format="%.6f", key="latitud")
        with col2:
            lon = st.number_input("Longitud", format="%.6f", key="longitud")

        if st.button("Obtener humedad y altitud"):
            if lat and lon:
                humedad = get_humidity(lat, lon)
                altitud = get_elevation(lat, lon)
                if humedad is not None:
                    st.session_state.humedad = humedad
                if altitud is not None:
                    st.session_state.altitud = altitud
            else:
                st.warning("Ingrese latitud y longitud válidas.")

    elif metodo == "Por ubicación actual":
        if st.button("📍 Detectar ubicación"):
            lat, lon, ciudad = get_location_from_ip()
            if lat and lon:
                st.session_state.latitud = lat
                st.session_state.longitud = lon
                st.session_state.ubicacion = ciudad
                humedad = get_humidity(lat, lon)
                altitud = get_elevation(lat, lon)
                if humedad is not None:
                    st.session_state.humedad = humedad
                if altitud is not None:
                    st.session_state.altitud = altitud
            else:
                st.warning("No se pudo detectar la ubicación.")
        
        st.info(f"📌 Ubicación detectada: {st.session_state.ubicacion}")
        st.write(f"Latitud: {st.session_state.latitud}, Longitud: {st.session_state.longitud}")

    # Mostrar campos manuales
    st.markdown("### Datos del suelo:")

    tipo_suelo = st.number_input("Tipo de suelo (número)", min_value=0, max_value=10, step=1)
    pH = st.number_input("pH", min_value=0.0, max_value=14.0, step=0.1)
    materia_organica = st.number_input("Materia orgánica (%)", min_value=0.0, step=0.1)
    conductividad = st.number_input("Conductividad", min_value=0.0, step=0.01)
    nitrogeno = st.number_input("Nitrógeno (mg/kg)", min_value=0.0, step=0.1)
    fosforo = st.number_input("Fósforo (mg/kg)", min_value=0.0, step=0.1)
    potasio = st.number_input("Potasio (mg/kg)", min_value=0.0, step=0.1)
    humedad = st.number_input("Humedad (%)", min_value=0.0, max_value=100.0, step=0.1, value=st.session_state.humedad)
    densidad = st.number_input("Densidad (g/cm³)", min_value=0.0, step=0.01)
    altitud = st.number_input("Altitud (m)", min_value=-500.0, max_value=9000.0, step=1.0, value=st.session_state.altitud)

    # Diccionario de nombres de cultivos
    cultivos = {
        0: "Trigo", 1: "Maíz", 2: "Arroz", 3: "Sorgo", 4: "Papa",
        5: "Cebada", 6: "Caña de azúcar", 7: "Soja", 8: "Yuca", 9: "Frijol", 10: "Avena"
    }

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("🌱 Predecir"):
            input_data = pd.DataFrame([{
                "tipo_suelo": tipo_suelo,
                "pH": pH,
                "materia_organica": materia_organica,
                "conductividad": conductividad,
                "nitrogeno": nitrogeno,
                "fosforo": fosforo,
                "potasio": potasio,
                "humedad": humedad,
                "densidad": densidad,
                "altitud": altitud
            }])

            fert_model, cult_model = load_models()
            column_order = ["tipo_suelo", "pH", "materia_organica", "conductividad",
                            "nitrogeno", "fosforo", "potasio", "humedad", "densidad", "altitud"]
            dmatrix = xgb.DMatrix(input_data[column_order], feature_names=column_order)

            fert_pred_prob = fert_model.predict(dmatrix)[0]
            fert_pred = int(fert_pred_prob >= 0.5)

            cult_pred_probs = cult_model.predict(dmatrix)[0]
            cult_pred_class = int(np.argmax(cult_pred_probs))
            cultivo_nombre = cultivos.get(cult_pred_class, "Desconocido")

            st.success(f"🌱 Fertilidad estimada: {fert_pred}")
            st.success(f"🌾 Cultivo recomendado: {cultivo_nombre}")
    
    with col2:
        if st.button("🧹 Limpiar"):
            for key in st.session_state.keys():
                st.session_state[key] = default_values.get(key, 0.0)
            st.experimental_rerun()

if __name__ == "__main__":
    main()



























