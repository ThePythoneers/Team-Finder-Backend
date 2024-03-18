from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def wait_for_element(driver, locator, timeout=10):
    try:
        return WebDriverWait(driver, timeout).until(EC.presence_of_element_located(locator))
    except:
        return None

driver = webdriver.Chrome()

driver.get("https://testing-ebon-chi.vercel.app/")

wait_for_element(driver, (By.CSS_SELECTOR, "input[name='username']"))

try:
    username_input = wait_for_element(driver, (By.CSS_SELECTOR, "input[name='username']"))
    username_input.send_keys("Team Finder")
    time.sleep(0.5)

    email_input = driver.find_element(By.CSS_SELECTOR, "input[name='email']")
    email_input.send_keys("example@example.com")
    time.sleep(0.5)

    password_input = driver.find_element(By.ID, "Password1@")
    password_input.send_keys("Password1@")
    time.sleep(0.5)

    organization_name_input = driver.find_element(By.CSS_SELECTOR, "input[name='organization_name']")
    organization_name_input.send_keys("ASSIST Software")
    time.sleep(0.5)

    hq_address_input = driver.find_element(By.CSS_SELECTOR, "input[name='hq_address']")
    hq_address_input.send_keys("Str. Zorilor")
    time.sleep(0.5)

    submit_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Sign Up')]")
    submit_button.click()
except Exception as e:
    pass

time.sleep(5)
driver.quit()

print("Script completed successfully.")
