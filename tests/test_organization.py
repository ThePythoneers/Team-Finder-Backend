from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import requests

driver = webdriver.Chrome()

try:
    driver.get("http://127.0.0.1:8000")

    payload ={
        "detail": [
            {
                "loc": "string",
                "msg": "string",
                "type": "string"
            }
        ]
    }
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json"
    }

    response = requests.post("http://127.0.0.1:8000/organization/", json=payload, headers=headers)

    response_json = response.json()
    assert response.status_code == 200
    assert "organization_info" in response_json
    print("Get Organization Info test passed!")

except AssertionError:
    print("Get Organization Info test failed!")

finally:
    driver.quit()
