import requests
import os

# Заголовки браузера (копируй из DevTools -> Network -> Headers)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.6 Safari/605.1.15",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://www.alibaba.com",
}

# URL, который отвечает за поиск товаров (замени на реальный из DevTools)
url = "https://www.alibaba.com/api/products/search?keywords=laptop"

image_path = os.path.abspath("../parser/img/rope1.png")
#
# # Отправляем GET-запрос
# response = requests.get(url, headers=HEADERS)

upload_url = "https://www.alibaba.com/picture/upload.htm"

files = {"file": open(image_path, "rb")}

# Отправляем POST-запрос
response = requests.post(upload_url, files=files, headers=HEADERS)

# Вывод JSON-ответа
print(response.url)