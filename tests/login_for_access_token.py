import requests


def test_register_employee():
    url = "http://127.0.0.1:8000/auth/employee/"
    payload = {
        "username": "test_user",
        "email": "test@example.com",
        "password": "testpassword"
    }

    response = requests.post(url, json=payload)

    if response.status_code == 200:
        print("Employee registration successful.")
    elif response.status_code == 422:
        print("Validation error occurred:", response.json())
    else:
        print("Unexpected status code:", response.status_code)


if __name__ == "__main__":
    test_register_employee()
