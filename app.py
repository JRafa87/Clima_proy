import streamlit as st
import requests
import pandas as pd
import numpy as np
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
        return float(data["main"]["humidity"]), data.get("name", "Ubicación desconocida")
    except:
        return None, "Ubicación desconocida"

# Inicializar claves del estado de sesión
def init_session_state(defaults):
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

# Predicción con nombres de columnas EXACTOS
def predict_fertility_and_cultivo(input_data, fertilidad_model, cultivo_model):
    column_order = [
        "tipo_suelo", "pH", "materia_organica", "conductividad",
        "nitrogeno", "fosforo", "potasio",
        "humedad", "densidad", "altitud"
    ]
    input_data.columns = column_order
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

def main():
    st.title("🌾 Predicción de Fertilidad y Cultivo")

    # Inicializar estado
    init_session_state({
        "humedad": 0.0,
        "altitud": 0.0,
        "latitud": 0.0,
        "longitud": 0.0,
        "ubicacion_nombre": "",
        "historial": []
    })

    metodo = st.radio("Método de ingreso de datos:", ["Por coordenadas", "Por ubicación actual", "Manual"])
    lat = lon = None

    if metodo == "Por coordenadas":
        col1, col2 = st.columns(2)
        with col1:
            st.session_state.latitud = st.number_input("Latitud", format="%.6f", key="lat_input")
        with col2:
            st.session_state.longitud = st.number_input("Longitud", format="%.6f", key="lon_input")

        if st.button("📍 Obtener humedad y altitud"):
            if st.session_state.latitud and st.session_state.longitud:
                humedad, nombre = get_humidity(st.session_state.latitud, st.session_state.longitud)
                altitud = get_elevation(st.session_state.latitud, st.session_state.longitud)
                if humedad is not None:
                    st.session_state.humedad = humedad
                if altitud is not None:
                    st.session_state.altitud = altitud
                st.session_state.ubicacion_nombre = nombre
            else:
                st.warning("Ingrese latitud y longitud válidas.")

    elif metodo == "Por ubicación actual":
        st.info("🌍 Función no implementada aún para navegador. Use coordenadas manuales por ahora.")

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

    # Diccionario de nombres de cultivos por ID
    cultivos = {
        0: "Trigo", 1: "Maíz", 2: "Arroz", 3: "Sorgo", 4: "Papa",
        5: "Cebada", 6: "Caña de azúcar", 7: "Soja", 8: "Yuca",
        9: "Frijol", 10: "Avena"
    }

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("✅ Predecir"):
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

            st.session_state.historial.append({
                "fertilidad": fert_pred,
                "cultivo": cultivo_nombre,
                "ubicacion": st.session_state.ubicacion_nombre or "Manual"
            })
def limpiar_campos():
    st.session_state.tipo_suelo = 0
    st.session_state.pH = 0.0
    st.session_state.materia_organica = 0.0
    st.session_state.conductividad = 0.0
    st.session_state.nitrogeno = 0.0
    st.session_state.fosforo = 0.0
    st.session_state.potasio = 0.0
    st.session_state.humedad = 0.0
    st.session_state.densidad = 0.0
    st.session_state.altitud = 0.0

    with col2:
        if st.button("🧹 Limpiar campos"):
          limpiar_campos()




    # Mostrar historial
    if st.session_state.historial:
        st.markdown("---")
        st.subheader("📋 Historial de predicciones")
        st.dataframe(pd.DataFrame(st.session_state.historial))

if __name__ == "__main__":
    main()



























