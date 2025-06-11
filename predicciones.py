import xgboost as xgb
import joblib  # Asegúrate de importar joblib

def load_models():
    try:
        # Cargar los modelos desde las rutas proporcionadas
        fertilidad_model = joblib.load("fertilidad_model.json")  # Asegúrate de colocar la ruta correcta
        cultivo_model = joblib.load("cultivo_model.json")  # Asegúrate de colocar la ruta correcta
        return fertilidad_model, cultivo_model
    except FileNotFoundError as e:
        # Si los archivos no se encuentran
        print(f"Error: No se pudo encontrar uno de los archivos de modelo. {str(e)}")
        return None, None
    except Exception as e:
        # Captura cualquier otro tipo de error
        print(f"Error al cargar los modelos: {str(e)}")
        return None, None

def predict_fertility_and_cultivo(input_data, fertilidad_model, cultivo_model):
    # Verificar si los modelos se cargaron correctamente
    if fertilidad_model is None or cultivo_model is None:
        raise ValueError("Los modelos no se cargaron correctamente. Verifica los archivos.")
    
    try:
        # Predicción de fertilidad
        fertilidad = int(fertilidad_model.predict(input_data)[0])
        predicted_fertilidad = "Fértil" if fertilidad == 1 else "Infértil"
        
        # Predicción del cultivo basado en la fertilidad
        predicted_cultivo = "Ninguno"
        if fertilidad == 1:
            cultivo = int(cultivo_model.predict(input_data)[0])
            # Lista de cultivos posibles, en función del modelo de cultivo
            cultivos = [
                "Trigo", "Maíz", "Caña de Azúcar", "Algodón", "Arroz", "Papa",
                "Cebolla", "Tomate", "Batata", "Brócoli", "Café"
            ]
            predicted_cultivo = cultivos[cultivo] if cultivo < len(cultivos) else "Desconocido"
        
        return predicted_fertilidad, predicted_cultivo
    except Exception as e:
        # Captura cualquier error durante la predicción
        print(f"Error en la predicción: {str(e)}")
        return "Error en la predicción", "Error en la predicción"



