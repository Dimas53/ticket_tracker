from fastapi.testclient import TestClient
from main import app
import pytest

client = TestClient(app)


def test_admin_flow():
    # 1. Регистрируем админа
    reg_response = client.post(
        "/register",
        json={"username": "admin_new_1234", "password": "123"}
    )
    assert reg_response.status_code == 200
    assert reg_response.json()["role"] == "admin"

    # 2. Получаем токен
    login_data = {
        "username": "admin_new_1234",
        "password": "123"
    }
    token_response = client.post("/token", data=login_data)
    assert token_response.status_code == 200
    token = token_response.json()["access_token"]

    # 3. Удаляем все тикеты с этим токеном
    auth_header = {"Authorization": f"Bearer {token}"}
    del_response = client.delete("/tickets", headers=auth_header)

    assert del_response.status_code == 200
    assert "deleted by admin" in del_response.json()["message"]


def test_user_forbidden():
    # Проверяем, что обычный юзер (без токена) не может удалять
    response = client.delete("/tickets")
    assert response.status_code == 401  # Unauthorized