import requests
API_KEY ="d17e26c2c185c3a078efc7baadae7d06"
lat, lon =6.9271, 79.8612

url=f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={API_KEY}"
response = requests.get(url)
data = response.json()
print(data)