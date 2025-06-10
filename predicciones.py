import xgboost as xgb
import joblib  # Asegúrate de importar joblib

def load_models():
    try:
        # Cargar los modelos desde las rutas proporcionadas
        fertilidad_model = joblib.load("ruta_a_tu_modelo_fertilidad.pkl")
        cultivo_model = joblib.load("ruta_a_tu_modelo_cultivo.pkl")
        return fertilidad_model, cultivo_model
    except Exception as e:
        print(f"Error al cargar los modelos: {str(e)}")
        return None, None

def predict_fertility_and_cultivo(input_data, fertilidad_model, cultivo_model):
    # Verificar si los modelos se cargaron correctamente
    if fertilidad_model is None or cultivo_model is None:
        raise ValueError("Los modelos no se cargaron correctamente. Verifica los archivos.")
    
    # Realizar las predicciones
    try:
        # Predicción de fertilidad
        fertilidad = int(fertilidad_model.predict(input_data)[0])
        predicted_fertilidad = "Fértil" if fertilidad == 1 else "Infértil"
        
        # Predicción del cultivo basado en la fertilidad
        predicted_cultivo = "Ninguno"
        if fertilidad == 1:
            cultivo = int(cultivo_model.predict(input_data)[0])
            cultivos = ["Trigo", "Maíz", "Caña de Azúcar", "Algodón", "Arroz", "Papa", "Cebolla", "Tomate", "Batata", "Brócoli", "Café"]
            predicted_cultivo = cultivos[cultivo] if cultivo < len(cultivos) else "Desconocido"
        
        return predicted_fertilidad, predicted_cultivo
    except Exception as e:
        print(f"Error en la predicción: {str(e)}")
        return "Error en la predicción", "Error en la predicción"


