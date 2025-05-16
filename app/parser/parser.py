from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from typing import List, Dict, Union
import time
import os
import re

def parse_alibaba_image(image_path: str) -> List[Dict[str, Union[str, float]]]:
    data = []

    def solve_captcha(driver):
        WebDriverWait(driver, 100).until(
            EC.presence_of_element_located((By.ID, "baxia-dialog-content"))
        )
        iframe = driver.find_element(By.ID, "baxia-dialog-content")
        driver.switch_to.frame(iframe)

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//span[contains(@class, 'btn_slide')]"))
        )
        slider = driver.find_element(By.XPATH, "//span[contains(@class, 'btn_slide')]")

        action = ActionChains(driver, duration=5)
        action.click_and_hold(slider)
        for i in range(0, 360, 10):
            try:
                action.move_by_offset(i, 0)
            except Exception:
                continue
        action.release().perform()
        action.click_and_hold(slider).pause(1).move_by_offset(360, 10).release().perform()

        driver.switch_to.default_content()

    alibaba_url = "https://www.alibaba.com/"
    options = webdriver.ChromeOptions()
    options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.6 Safari/605.1.15")
    options.add_argument("--disable-blink-features=AutomationControlled")
    # options.add_argument("--headless")
    # options.add_argument("--disable-gpu")
    # options.add_argument("--no-sandbox")
    # options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)

    try:
        driver.get(alibaba_url)

        # solve_captcha(driver)

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "img-upload-button"))
        ).click()

        upload_input = driver.find_element(By.XPATH, "//input[@type='file']")
        upload_input.send_keys(os.path.abspath(image_path))

        offer_list = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "img-search-offer-list"))
        )

        offers = offer_list.find_elements(By.XPATH, "./div")[:10]

        for i in range(len(offers)):
            try:
                time.sleep(5)
                offer_list = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "img-search-offer-list"))
                )
                offers = offer_list.find_elements(By.XPATH, "./div")
                result = offers[i]

                seller_url = result.find_element(By.TAG_NAME, "a").get_attribute("href")
                images = result.find_elements(By.TAG_NAME, "img")
                image_url = images[1].get_attribute("src")
                print(0)

                rating_score = result.find_element(By.CLASS_NAME, "search-card-e-review")
                rating = float(rating_score.find_element(By.XPATH, "./strong").text)
                years_text = result.find_element(By.CLASS_NAME, "margin-right-2").text
                years = float(re.search(r"\d+(?:[\.,]\d+)?", years_text.replace(",", ".")).group(0))

                driver.get(seller_url)

                price_rows = driver.find_elements(By.XPATH, "//div[contains(@class, 'price-item')]")

                company_element = driver.find_element(By.CSS_SELECTOR, "span.company-name a")

                company_name = company_element.text.strip()
                supplier_url = company_element.get_attribute("href")

                min_price = 100000.0
                min_quantity = "0"

                for row in price_rows:
                    try:
                        price_element = driver.find_element(By.CSS_SELECTOR, ".id-flex-col.id-text-2xl.id-font-bold")
                        price = price_element.text.strip()
                        print(price)
                        # quantity_element = driver.find_element(By.XPATH,"//div[@class='price-item']//div[contains(text(), 'шт.')]")
                        # quantity = quantity_element.text.strip()
                        # print(quantity)
                        price_float = float(re.sub(r"[^\d.]", "", price.replace(",", ".")))
                        quantity_clean = 1000

                        print(3)

                        if price_float < min_price:
                            min_price = price_float
                            min_quantity = quantity_clean

                    except Exception as e:
                        print(f"Ошибка при разборе строки: {e}")
                        continue

                if min_price == 100000.0:
                    try:
                        min_price = 10

                        # quantity_block = driver.find_element(By.CSS_SELECTOR, "div.id-mb-2.id-text-sm")
                        # lines = quantity_block.text.strip().split("\n")
                        # min_quantity = next((re.search(r"\d+", l).group() for l in lines if re.search(r"\d+", l)), "0")
                        min_quantity = 1000
                    except Exception as e:
                        print("Альтернативный парсинг цены не удался:", e)

                if min_price == 100000.0:
                    continue

                data.append({
                    "image": image_url,
                    "price": min_price,
                    "min_quantity": min_quantity,
                    "rating": rating,
                    "years": years,
                    "url": seller_url,
                    "supplier_url": supplier_url,
                    "supplier_name": company_name,
                })

                driver.back()

            except Exception as e:
                print(f"Error extracting data: {e}")
                continue

    except Exception as e:
        print(f"Unexpected error in parse_alibaba_image: {e}")

    finally:
        driver.quit()

    return data
