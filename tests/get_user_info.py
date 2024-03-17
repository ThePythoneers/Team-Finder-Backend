import requests


def test_get_user_info():
    url = "http://127.0.0.1:8000/user/get/"
    valid_user_id = "example_user_id"
    invalid_user_id = "123"

    response = requests.get(url.format(user_id=valid_user_id))
    if response.status_code == 200:
        print("Successful Response:")
        print(response.json())
    elif response.status_code == 422:
        print("Validation Error:", response.json())
    else:
        print("Unexpected status code:", response.status_code)

    # Testing with invalid user ID
    response = requests.get(url.format(user_id=invalid_user_id))
    if response.status_code == 200:
        print("Successful Response (Invalid User ID):")
        print(response.json())
    elif response.status_code == 422:
        print("Validation Error (Invalid User ID):", response.json())
    else:
        print("Unexpected status code (Invalid User ID):", response.status_code)


if __name__ == "__main__":
    test_get_user_info()
