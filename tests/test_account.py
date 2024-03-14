from fastapi.testclient import TestClient
import pytest, sys

sys.path.insert(1, "E:\\ASSIST TECH CHALLENGE\\api")

from main import app


client = TestClient(app)


def test_get_user():
    response = client.get("/user/get/{invaliduuid}")
    assert response.status_code == 400
