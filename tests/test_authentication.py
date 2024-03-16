from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import requests

driver = webdriver.Chrome()

try:
    driver.get("http://127.0.0.1:8000")

    payload = {
        "username": "lep[",
        "email": "string",
        "password": "string",
        "organization_name": "string",
        "hq_address": "string"
    }
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json"
    }

    response = requests.post("http://127.0.0.1:8000/auth/register/organization", json=payload, headers=headers)

    response_json = response.json()

    assert response_json["message"] == "Organization registration successful."

    print("Organization registration test passed!")

finally:
    driver.quit()