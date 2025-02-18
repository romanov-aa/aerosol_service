import requests

# URL вашего API
url = 'http://127.0.0.1:5000/predict'

# Данные, которые вы хотите отправить
data = {
    "aot" : {
        "440nm" : 0.4025,
        "675nm" : 0.1927,
        "870nm" : 0.12245,
        "1020nm" : 0.0945
    },
    "ang" : 1.749413,
    "lr" : 39.302,
    "dpr" : 0.010105,
    "coord" : {
        "lat" : 40.821313,
        "lon" : -73.949036
    }
}

# Отправка POST-запроса
response = requests.post(url, json=data)

# Проверка статуса ответа
if response.status_code == 200:
    # Получение данных из ответа
    result = response.json()
    print('Результат:', result['result'])
else:
    print('Ошибка:', response.status_code, response.text)

