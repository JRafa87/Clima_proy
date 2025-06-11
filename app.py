import streamlit as st
import requests
import pandas as pd
import xgboost as xgb

# Función para obtener la altitud
def get_elevation(lat, lon):
    try:
        url = f"https://api.open-elevation.com/api/v1/lookup?locations={lat},{lon}"
        response = requests.get(url)
        data = response.json()
        return float(data['results'][0]['elevation'])
    except:
        return None

# Función para obtener la humedad (OpenWeatherMap)
def get_humidity(lat, lon):
    api_key = "f75c529787e26621bbd744dd67c056b0"
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
        return float(data["main"]["humidity"])
    except:
        return None

# Predicción con nombres de columnas EXACTOS
def predict_fertility_and_cultivo(input_data, fertilidad_model, cultivo_model):
    # Orden y nombres EXACTOS usados en el modelo entrenado
    column_order = [
        "tipo_suelo", "pH", "materia_organica", "conductividad",
        "nitrogeno", "fosforo", "potasio",
        "humedad", "densidad", "altitud"
    ]
    
    # Asegurar orden y nombres exactos
    input_data.columns = column_order  # Sobrescribe directamente si viene en orden
    dmatrix = xgb.DMatrix(input_data, feature_names=column_order)
    
    fert_pred = fertilidad_model.predict(dmatrix)
    cult_pred = cultivo_model.predict(dmatrix)
    return fert_pred, cult_pred


# Cargar modelos correctamente
def load_models():
    fertilidad_model = xgb.Booster()
    cultivo_model = xgb.Booster()
    fertilidad_model.load_model("fertilidad_model.json")
    cultivo_model.load_model("cultivo_model.json")
    return fertilidad_model, cultivo_model


# Inicializar session_state
if 'humedad' not in st.session_state:
    st.session_state.humedad = 0.0
if 'altitud' not in st.session_state:
    st.session_state.altitud = 0.0

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
        st.info("🌍 Función no implementada aún.")

    # Mostrar todos los campos
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

    

    if st.button("Predecir"):
        input_data = pd.DataFrame([{
            "tipo_suelo": tipo_suelo,
            "ph": pH,
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
        fert_pred, cult_pred = predict_fertility_and_cultivo(input_data, fert_model, cult_model)

        st.success(f"🌱 Fertilidad estimada: {fert_pred[0]}")
        st.success(f"🌾 Cultivo recomendado: {cult_pred[0]}")


if __name__ == "__main__":
    main()

























