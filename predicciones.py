# predicciones.py
import xgboost as xgb

def load_models():
    # Cargar el modelo de fertilidad
    fertilidad_model = xgb.XGBClassifier()
    fertilidad_model.load_model('fertilidad_model.json')

    # Cargar el modelo de cultivo
    cultivo_model = xgb.XGBClassifier()
    cultivo_model.load_model('cultivo_model.json')

    return fertilidad_model, cultivo_model

def predict_fertility_and_cultivo(input_data, fertilidad_model, cultivo_model):
    # Realizar las predicciones
    fertilidad = int(fertilidad_model.predict(input_data)[0])
    predicted_fertilidad = "Fértil" if fertilidad == 1 else "Infértil"
    
    predicted_cultivo = "Ninguno"
    if fertilidad == 1:
        cultivo = int(cultivo_model.predict(input_data)[0])
        cultivos = ["Trigo", "Maíz", "Caña de Azúcar", "Algodón", "Arroz", "Papa", "Cebolla", "Tomate", "Batata", "Brócoli", "Café"]
        predicted_cultivo = cultivos[cultivo] if cultivo < len(cultivos) else "Desconocido"
    
    return predicted_fertilidad, predicted_cultivo

