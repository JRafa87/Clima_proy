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
    except Exception as e:
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
    except Exception as e:
        return None

# Cargar modelos
def load_models():
    fertilidad_model = xgb.Booster()
    fertilidad_model.load_model('fertilidad_model.json')
    cultivo_model = xgb.Booster()
    cultivo_model.load_model('cultivo_model.json')
    return fertilidad_model, cultivo_model

# Realizar predicciones
def predict_fertility_and_cultivo(input_data, fertilidad_model, cultivo_model):
    dmatrix = xgb.DMatrix(input_data)
    fert_pred = fertilidad_model.predict(dmatrix)
    crop_pred = cultivo_model.predict(dmatrix)
    return fert_pred, crop_pred

# Interfaz principal
def main():
    st.title("🌾 Predicción de Fertilidad del Suelo y Cultivo Recomendado")

    st.markdown("### Seleccione cómo desea ingresar los datos")
    metodo = st.radio("Método de entrada", ["Por coordenadas", "Por ubicación actual", "Manual"])

    lat = lon = None
    humedad = altitud = None

    if metodo == "Por coordenadas":
        col1, col2 = st.columns(2)
        with col1:
            lat = st.number_input("Latitud", format="%.6f")
        with col2:
            lon = st.number_input("Longitud", format="%.6f")
        
        if st.button("Obtener humedad y altitud"):
            if lat and lon:
                humedad = get_humidity(lat, lon)
                altitud = get_elevation(lat, lon)
                if humedad is None or altitud is None:
                    st.warning("No se pudieron obtener todos los datos desde la ubicación.")
            else:
                st.warning("Por favor, ingrese coordenadas válidas.")

    elif metodo == "Por ubicación actual":
        st.info("🌍 Funcionalidad de ubicación actual no implementada aún.")

    # Campos siempre visibles
    st.markdown("### Ingrese los datos del suelo")

    tipo_suelo = st.selectbox("Tipo de suelo", ["Arcilloso", "Arenoso", "Franco", "Limoso"])
    ph = st.number_input("pH", min_value=0.0, max_value=14.0, step=0.1)
    materia_organica = st.number_input("Materia orgánica (%)", min_value=0.0, step=0.1)
    conductividad = st.number_input("Conductividad eléctrica (dS/m)", min_value=0.0, step=0.01)
    nitrogeno = st.number_input("Nitrógeno (mg/kg)", min_value=0.0, step=0.1)
    fosforo = st.number_input("Fósforo (mg/kg)", min_value=0.0, step=0.1)
    potasio = st.number_input("Potasio (mg/kg)", min_value=0.0, step=0.1)

    # Humedad y altitud con valores por defecto (de las APIs si se obtuvieron)
    humedad = st.number_input("Humedad (%)", min_value=0.0, max_value=100.0, step=0.1, value=humedad if humedad else 0.0)
    altitud = st.number_input("Altitud (m)", min_value=-500.0, max_value=9000.0, step=1.0, value=altitud if altitud else 0.0)

    densidad = st.number_input("Densidad aparente (g/cm³)", min_value=0.0, step=0.01)

    if st.button("Predecir"):
        # Convertir tipo de suelo a número (codificación simple)
        tipo_suelo_cod = {"Arcilloso": 0, "Arenoso": 1, "Franco": 2, "Limoso": 3}[tipo_suelo]

        input_data = pd.DataFrame([{
            "tipo_suelo": tipo_suelo_cod,
            "ph": ph,
            "materia_organica": materia_organica,
            "conductividad": conductividad,
            "nitrogeno": nitrogeno,
            "fosforo": fosforo,
            "potasio": potasio,
            "humedad": humedad,
            "altitud": altitud,
            "densidad": densidad
        }])

        fertilidad_model, cultivo_model = load_models()
        fert_pred, crop_pred = predict_fertility_and_cultivo(input_data, fertilidad_model, cultivo_model)

        st.success(f"🌱 Fertilidad estimada: {fert_pred[0]:.2f}")
        st.success(f"🌾 Cultivo recomendado (ID): {int(crop_pred[0])}")

if __name__ == "__main__":
    main()






















