import requests


def test_get_user_skills():
    url = "http://127.0.0.1:8000/user/skills"

    # Assuming authentication headers are required for the logged-in user
    headers = {
        "Authorization": "Bearer YOUR_ACCESS_TOKEN_HERE"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        print("Successful Response:")
        print(response.json())
    else:
        print("Unexpected status code:", response.status_code)


if __name__ == "__main__":
    test_get_user_skills()
    