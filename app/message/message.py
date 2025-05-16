import time

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def click_chat_button(driver):
    buttons = driver.find_elements(By.TAG_NAME, "button")

    for b in buttons:
        text = b.text.strip()
        if text == "Начать чат":
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", b)
            time.sleep(1)

            actions = ActionChains(driver)
            actions.move_to_element(b).pause(0.5).click().perform()

def handle_login_popup(driver, email, password):
    wait = WebDriverWait(driver, 10)
    login_btn = wait.until(
        EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "span[class^='SignTips_module_lineText']")
        )
    )
    actions = ActionChains(driver)
    actions.move_to_element(login_btn).pause(0.5).click().perform()
    login_btn.click()

    email_input = wait.until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "input[name='account']"))
    )
    email_input.clear()
    email_input.send_keys(email)
    time.sleep(1)

    password_input = driver.find_element(By.CSS_SELECTOR, "input[name='password']")
    password_input.clear()
    password_input.send_keys(password)
    time.sleep(1)

    login_button = wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "button.xman-button-primary"))
    )
    actions = ActionChains(driver)
    actions.move_to_element(login_button).pause(0.5).click().perform()
    login_button.click()

    # try:
    #     email_input = wait.until(
    #         EC.visibility_of_element_located((By.CSS_SELECTOR, "input[name='account']"))
    #     )
    #     email_input.clear()
    #     email_input.send_keys(email)
    #     time.sleep(1)
    #
    #     password_input = driver.find_element(By.CSS_SELECTOR, "input[name='password']")
    #     password_input.clear()
    #     password_input.send_keys(password)
    #     time.sleep(1)
    #
    #     login_button = wait.until(
    #         EC.element_to_be_clickable((By.CSS_SELECTOR, "button.xman-button-primary"))
    #     )
    #     actions = ActionChains(driver)
    #     actions.move_to_element(login_button).pause(0.5).click().perform()
    #     login_button.click()
    #
    # except TimeoutException:
    #     try:
    #         email_input = wait.until(EC.presence_of_element_located((By.NAME, "account")))
    #         email_input.clear()
    #         email_input.send_keys("yzaitseva2001@gmail.com")
    #
    #         password_input = wait.until(EC.presence_of_element_located((By.NAME, "password")))
    #         password_input.clear()
    #         password_input.send_keys("wigjar-1gommi-wisKyr")
    #         close_login_if_present(driver)
    #
    #         registration_button = wait.until(
    #             EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'tnh-sign-in')]"))
    #         )
    #         registration_button.click()
    #
    #     except Exception as e:
    #         print("Не удалось авторизоваться: ", e)



def close_login_if_present(driver):
    wait = WebDriverWait(driver, 10)
    try:
        continue_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.xsi_button"))
        )

        if continue_button.is_displayed():
            continue_button.click()
            print("Всплывающее окно логина закрыто.")

    except TimeoutException:
        login_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "sif_form-submit")))
        login_button.click()

def message(url: str):
    options = webdriver.ChromeOptions()
    options.add_argument(
        "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.6 Safari/605.1.15")
    options.add_argument("--disable-blink-features=AutomationControlled")
    # options.add_argument("--headless")
    # options.add_argument("--disable-gpu")
    # options.add_argument("--no-sandbox")
    # options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 10)

    driver.get(url)
    buttons = driver.find_elements(By.TAG_NAME, "button")
    click_chat_button(driver)

    handle_login_popup(driver, email="yzaitseva2001@gmail.com", password="wigjar-1gommi-wisKyr")
    driver.switch_to.default_content()

    time.sleep(5)

    iframe = wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "iframe[src*='message/weblite']"))
    )
    driver.switch_to.frame(iframe)

    message_input = wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'textarea.send-textarea'))
    )
    message_input.clear()
    message_input.send_keys(
        "Good day. Please send me the price list for this product and quantity requirements. Thank you.")

    time.sleep(1000)