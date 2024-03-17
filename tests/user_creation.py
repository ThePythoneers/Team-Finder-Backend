import requests


def test_register_organization():
    url = "http://127.0.0.1:8000/auth/register/organization"
    # Valid payload
    valid_payload = {
        "username": "test_user",
        "email": "testtest@example.com",
        "password": "testpassworD1+",
        "organization_name": "TestOrganization",
        "hq_address": "123TestSt"
    }

    invalid_payload_missing_email = {
        "username": "test_user",
        "password": "testpassword",
        "organization_name": "TestOrganization",
        "hq_address": "123TestSt"
    }

    invalid_payload_invalid_email = {
        "username": "test_user",
        "email": "invalidemail.com",
        "password": "testpassword",
        "organization_name": "TestOrganization",
        "hq_address": "12estSt"
    }

    invalid_payload_short_password = {
        "username": "test_user",
        "email": "test@example.com",
        "password": "1234567",
        "organization_name": "TestOrganization",
        "hq_address": "123TestSt"
    }

    invalid_payload_long_organization_name = {
        "username": "test_user",
        "email": "test@example.com",
        "password": "testpassword",
        "organization_name": "Very Long Organization Name That Exceeds Character Limit",
        "hq_address": "123TestSt"
    }

    response = requests.post(url, json=valid_payload)
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "token_type" in response.json()
    assert response.json()["token_type"] == "bearer"
    print("Registration successful with valid payload:", response.json()["access_token"])

    response = requests.post(url, json=invalid_payload_missing_email)
    assert response.status_code == 422
    assert "detail" in response.json()
    assert len(response.json()["detail"]) == 1
    assert "loc" in response.json()["detail"][0]
    assert "msg" in response.json()["detail"][0]
    assert "type" in response.json()["detail"][0]
    print("Validation error detected with missing email:", response.json()["detail"][0]["msg"])

    response = requests.post(url, json=invalid_payload_invalid_email)
    assert response.status_code == 422
    assert "detail" in response.json()
    assert len(response.json()["detail"]) == 1
    assert "loc" in response.json()["detail"][0]
    assert "msg" in response.json()["detail"][0]
    assert "type" in response.json()["detail"][0]
    print("Validation error detected with invalid email format:", response.json()["detail"][0]["msg"])

    response = requests.post(url, json=invalid_payload_short_password)
    assert response.status_code == 422
    assert "detail" in response.json()
    assert len(response.json()["detail"]) == 1
    assert "loc" in response.json()["detail"][0]
    assert "msg" in response.json()["detail"][0]
    assert "type" in response.json()["detail"][0]
    print("Validation error detected with short password:", response.json()["detail"][0]["msg"])

    response = requests.post(url, json=invalid_payload_long_organization_name)
    assert response.status_code == 422
    assert "detail" in response.json()
    assert len(response.json()["detail"]) == 1
    assert "loc" in response.json()["detail"][0]
    assert "msg" in response.json()["detail"][0]
    assert "type" in response.json()["detail"][0]
    print("Validation error detected with long organization name:", response.json()["detail"][0]["msg"])


if __name__ == "__main__":
    test_register_organization()