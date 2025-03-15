from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
import time
import os
from Producer import KafkaAvroProducer

KAFKA_BROKER = "localhost:9092"
SCHEMA_REGISTRY_URL = "http://localhost:8081"
TOPIC = "product-data"
SCHEMA_PATH = "product_schema.avsc"

def solve_captcha():
    # ✅ Ожидаем появления iframe с капчей
    WebDriverWait(driver, 100).until(
        EC.presence_of_element_located((By.ID, "baxia-dialog-content"))
    )

    # 🔄 Переключаемся в iframe с капчей
    iframe = driver.find_element(By.ID, "baxia-dialog-content")
    driver.switch_to.frame(iframe)
    print("✅ Переключились в iframe")

    # 🖱️ Ожидаем и находим ползунок
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//span[contains(@class, 'btn_slide')]"))
    )
    slider = driver.find_element(By.XPATH, "//span[contains(@class, 'btn_slide')]")

    # 🚀 Двигаем ползунок вправо
    action = ActionChains(driver, duration=5)
    action.click_and_hold(slider)
    for i in range(0, 360, 10):
        try:
            action.move_by_offset(i, 0)
        except Exception as e:
            continue
    action.release()
    action.perform()
    action.click_and_hold(slider).pause(1).move_by_offset(360, 10).release().perform()
    print("✅ Ползунок перемещен!")

    # 🔄 Возвращаемся обратно в основное окно
    driver.switch_to.default_content()
    print("✅ Вернулись в основное окно")

alibaba_url = "https://www.alibaba.com/"

# Путь к изображению для загрузки
image_path = os.path.abspath("img/rope1.png")

# Настройка WebDriver
options = webdriver.ChromeOptions()
options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.6 Safari/605.1.15")
options.add_argument("--disable-blink-features=AutomationControlled")

driver = webdriver.Chrome(options=options)

try:
    driver.get(alibaba_url)
    time.sleep(5)

    # solve_captcha()

    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "img-upload-button")))
    driver.find_element(By.XPATH, "//div[contains(@class, 'img-upload-button')]").click()
    time.sleep(3)
    upload_input = driver.find_element(By.XPATH, "//input[@type='file']")
    upload_input.send_keys(image_path)
    time.sleep(5)

    # Ждём загрузки результатов
    offer_list = (WebDriverWait(driver, 10)
                  .until(EC.presence_of_element_located((By.CLASS_NAME, "img-search-offer-list"))))

    # Получаем все предложения
    offers = offer_list.find_elements(By.XPATH, "./div")[:5]
    data = []

    for i in range(5):
        try:
            offer_list = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "img-search-offer-list"))
            )
            offers = offer_list.find_elements(By.XPATH, "./div")
            result = offers[i]

            # Извлекаем данные
            seller_url = result.find_element(By.TAG_NAME, "a").get_attribute("href")
            image_url = result.find_element(By.TAG_NAME, "img").get_attribute("src")
            price = result.find_element(By.CLASS_NAME, "search-card-e-price-main").text

            rating_score = result.find_element(By.CLASS_NAME, "search-card-e-review")
            rating = rating_score.find_element(By.XPATH, "./strong").text

            years = result.find_element(By.CLASS_NAME, "margin-right-2").text

            driver.get(seller_url)
            time.sleep(5)

            price_block = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "price-list"))
            )
            price_rows = driver.find_elements(By.XPATH, "//div[contains(@class, 'price-item')]")

            min_price = None
            min_quantity = None

            # Проходим по строкам таблицы цен
            for row in price_rows:
                try:
                    # Находим цену
                    price_value = row.find_element(By.XPATH, ".//div[contains(@class, 'price')]").text

                    # Находим количество товара для этой цены
                    quantity = row.find_element(By.XPATH, ".//div[contains(@class, 'quality')]").text

                    # Преобразуем цену и количество в числа
                    price_float = float(price_value.replace("$", "").replace(",", ".").strip())

                    # Определяем минимальную цену
                    if min_price is None or price_float < min_price:
                        min_price = price_float
                        min_quantity = quantity
                except Exception as e:
                    print(f"Ошибка при разборе цены: {e}")
                    continue

            data.append({
                "image": image_url,
                "price_main": price,  # Цена из поиска
                "min_price": min_price,  # Минимальная цена на странице товара
                "min_quantity": min_quantity,
                "rating": rating,
                "years": years,
                "url": seller_url
            })

            driver.back()

        except Exception as e:
            print(f"Error extracting data: {e}")
            continue

    # Печатаем данные
    for item in data:
        print(item)


    # Создание экземпляра продюсера
    producer = KafkaAvroProducer(KAFKA_BROKER, SCHEMA_REGISTRY_URL, TOPIC, SCHEMA_PATH)


finally:
    # Закрываем браузер
    driver.quit()

