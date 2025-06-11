import streamlit as st
import pandas as pd
import xgboost as xgb
import requests

st.set_page_config(page_title="Predicción de Fertilidad y Cultivo", layout="centered")

# === Función para cargar modelos ===
@st.cache_resource
def cargar_modelos():
    fert_model = xgb.Booster()
    fert_model.load_model("modelo_fertilidad.json")

    cult_model = xgb.Booster()
    cult_model.load_model("modelo_cultivo.json")

    return fert_model, cult_model

# === Función para obtener clima y altitud ===
def obtener_clima_y_altitud(lat, lon=None):
    try:
        if lon is None:
            # Si se pasó una ubicación (texto)
            response = requests.get(f"https://nominatim.openstreetmap.org/search?q={lat}&format=json").json()
            if response:
                lat = response[0]["lat"]
                lon = response[0]["lon"]
            else:
                return None, None
        # Simulación o reemplazo con API real
        # Por ahora valores fijos de ejemplo:
        #humedad = 52.0
        #altitud = 150.0
        #return humedad, altitud
    #except:
        #return None, None

# === Función para predecir ===
def predecir(input_df, fert_model, cult_model):
    columnas = [
        "tipo_suelo", "ph", "materia_organica", "conductividad",
        "nitrogeno", "fosforo", "potasio", "humedad",
        "densidad", "altitud"
    ]
    dmatrix = xgb.DMatrix(input_df[columnas], feature_names=columnas)
    fert_pred = fert_model.predict(dmatrix)
    cult_pred = cult_model.predict(dmatrix)
    return fert_pred, cult_pred

# === Interfaz principal ===
def main():
    st.title("🌱 Predicción de Fertilidad del Suelo y Cultivo Recomendado")

    metodo = st.radio("Método de ingreso:", ["Manual", "Por Coordenadas", "Por Ubicación"])
    humedad, altitud = None, None

    if metodo == "Por Coordenadas":
        lat = st.number_input("Latitud", format="%.6f", key="lat")
        lon = st.number_input("Longitud", format="%.6f", key="lon")

        if lat and lon:
            humedad, altitud = obtener_clima_y_altitud(lat, lon)
            if humedad is not None:
                st.success(f"Humedad: {humedad}%, Altitud: {altitud} m")
            else:
                st.warning("No se pudo obtener datos desde las coordenadas.")
    elif metodo == "Por Ubicación":
        ubicacion = st.text_input("Ubicación", key="ubicacion")
        if ubicacion:
            humedad, altitud = obtener_clima_y_altitud(ubicacion)
            if humedad is not None:
                st.success(f"Humedad: {humedad}%, Altitud: {altitud} m")
            else:
                st.warning("No se pudo obtener datos desde la ubicación.")

    st.subheader("📋 Datos del suelo")

    tipo_suelo = st.number_input("Tipo de suelo (número)", key="tipo_suelo")
    ph = st.number_input("pH", key="ph")
    materia_organica = st.number_input("Materia orgánica (%)", key="materia_organica")
    conductividad = st.number_input("Conductividad (dS/m)", key="conductividad")
    nitrogeno = st.number_input("Nitrógeno (mg/kg)", key="nitrogeno")
    fosforo = st.number_input("Fósforo (mg/kg)", key="fosforo")
    potasio = st.number_input("Potasio (mg/kg)", key="potasio")
    densidad = st.number_input("Densidad (g/cm³)", key="densidad")

    humedad = st.number_input("Humedad (%)", value=humedad or 0.0, key="humedad")
    altitud = st.number_input("Altitud (m)", value=altitud or 0.0, key="altitud")

    if st.button("🔍 Predecir"):
        try:
            input_df = pd.DataFrame([{
                "tipo_suelo": tipo_suelo,
                "ph": ph,
                "materia_organica": materia_organica,
                "conductividad": conductividad,
                "nitrogeno": nitrogeno,
                "fosforo": fosforo,
                "potasio": potasio,
                "humedad": humedad,
                "densidad": densidad,
                "altitud": altitud
            }])

            fert_model, cult_model = cargar_modelos()
            fert, cult = predecir(input_df, fert_model, cult_model)

            st.success(f"🌾 Fertilidad estimada: {fert[0]:.2f}")
            st.success(f"🌽 Cultivo recomendado: {cult[0]:.0f}")
        except Exception as e:
            st.error(f"Ocurrió un error: {e}")

if __name__ == "__main__":
    main()
























