import streamlit as st
import requests
import pandas as pd
import xgboost as xgb

# Obtener altitud desde Open Elevation API
def get_elevation(lat, lon):
    url = f"https://api.open-elevation.com/api/v1/lookup?locations={lat},{lon}"
    response = requests.get(url)
    data = response.json()
    elevation = data['results'][0]['elevation']
    return float(elevation)

# Obtener humedad desde OpenWeatherMap
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
        return {"error": str(e)}

# Cargar modelos
def load_models():
    fertilidad_model = xgb.Booster()
    fertilidad_model.load_model('fertilidad_model.json')
    cultivo_model = xgb.Booster()
    cultivo_model.load_model('cultivo_model.json')
    return fertilidad_model, cultivo_model

# Predicción
def predict_fertility_and_cultivo(input_data, fertilidad_model, cultivo_model):
    dmatrix = xgb.DMatrix(input_data)
    fert = fertilidad_model.predict(dmatrix)
    crop = cultivo_model.predict(dmatrix)
    return fert, crop

# App principal
def main():
    st.title("🌿 Predicción de Fertilidad del Suelo")

    st.markdown("### Seleccione el método para obtener los datos")
    method = st.radio("Método de entrada", ["Por coordenadas", "Por ubicación actual", "Manualmente"])

    lat = lon = humidity = elevation = None

    if method == "Por coordenadas":
        col1, col2 = st.columns(2)
        with col1:
            lat = st.number_input("Latitud", format="%.6f")
        with col2:
            lon = st.number_input("Longitud", format="%.6f")

        if st.button("Obtener datos automáticamente"):
            if lat and lon:
                humidity_result = get_humidity(lat, lon)
                elevation_result = get_elevation(lat, lon)

                if isinstance(humidity_result, dict) and "error" in humidity_result:
                    st.error(humidity_result["error"])
                else:
                    humidity = humidity_result
                    elevation = elevation_result
            else:
                st.warning("Por favor, ingresa latitud y longitud válidas.")

    elif method == "Por ubicación actual":
        st.info("📍 Funcionalidad aún no implementada.")
        # Aquí podrías simular valores en el futuro

    # Mostrar SIEMPRE los campos para inspección o edición
    humidity = st.number_input("Humedad del ambiente (%)", value=humidity if humidity is not None else 0.0, min_value=0.0, max_value=100.0)
    elevation = st.number_input("Altitud (m)", value=elevation if elevation is not None else 0.0, min_value=-500.0, max_value=9000.0)

    if st.button("Predecir Fertilidad y Cultivo"):
        input_data = pd.DataFrame({
            "humidity": [humidity],
            "elevation": [elevation]
        })

        fertilidad_model, cultivo_model = load_models()
        fert_pred, crop_pred = predict_fertility_and_cultivo(input_data, fertilidad_model, cultivo_model)

        st.success(f"🔬 Fertilidad estimada: {fert_pred[0]:.2f}")
        st.success(f"🌾 Cultivo recomendado (ID): {crop_pred[0]:.0f}")  # Puedes mapear el ID si lo deseas

if __name__ == "__main__":
    main()





















