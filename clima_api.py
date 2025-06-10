import requests

# Función para obtener los datos del clima
def get_weather_data(lat, lon):
    api_key = "f75c529787e26621bbd744dd67c056b0"  # Reemplaza con tu propia API Key de OpenWeather
    base_url = "https://api.openweathermap.org/data/2.5/weather"
    
    # Parámetros para la consulta
    params = {
        "lat": lat,
        "lon": lon,
        "appid": api_key,
        "units": "metric",  # Para obtener la temperatura en grados Celsius
        "lang": "es"  # Respuesta en español
    }
    
    try:
        # Hacer la solicitud GET
        response = requests.get(base_url, params=params)
        data = response.json()
        
        # Verificar si la respuesta es exitosa
        if response.status_code == 200:
            # Extraer los datos relevantes
            temperature = data['main']['temp']
            humidity = data['main']['humidity']
            wind_speed = data['wind']['speed']
            
            # Crear un diccionario con los datos
            weather_data = {
                'temperature': temperature,
                'humidity': humidity,
                'wind_speed': wind_speed
            }
            return weather_data
        else:
            return {'error': f"Error en la solicitud: {data['message']}"}
    except Exception as e:
        return {'error': f"Error al obtener los datos: {str(e)}"}

