import xgboost as xgb

# Carga tus modelos preentrenados de fertilidad y cultivo
fertilidad_model = xgb.XGBClassifier()
fertilidad_model.load_model("fertilidad_model.json")

cultivo_model = xgb.XGBClassifier()
cultivo_model.load_model("cultivo_model.json")

def predict_fertility_and_cultivo(input_data):
    """Hace las predicciones usando los modelos XGBoost"""
    predicted_fertilidad = int(fertilidad_model.predict(input_data)[0])
    predicted_fertilidad_text = "Fértil" if predicted_fertilidad == 1 else "Infértil"
    
    predicted_cultivo = "Ninguno"
    if predicted_fertilidad == 1:
        predicted_cultivo_encoded = int(cultivo_model.predict(input_data)[0])
        cultivos = ["Trigo", "Maíz", "Caña de Azúcar", "Algodón", "Arroz", "Papa", "Cebolla", "Tomate", "Batata", "Brócoli", "Café"]
        predicted_cultivo = cultivos[predicted_cultivo_encoded] if predicted_cultivo_encoded < len(cultivos) else "Desconocido"
    
    return (predicted_fertilidad_text, predicted_cultivo)
