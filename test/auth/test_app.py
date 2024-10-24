from app import app
from fastapi.testclient import TestClient
from pydantic import ValidationError
import pytest
from schemas.auth.AppSchema import AppBase, AppsResponse
from utils.settings import Settings

# Environment Configuration
settings = Settings()
TESTS_TOKEN = settings.tests_token

client = TestClient(app)


@pytest.fixture
def token():
    return f"Bearer {TESTS_TOKEN}"


class TestApp:
    client = TestClient(app)

    def test_get_not_authenticated(self):
        response = self.client.get("/api/admin/app")
        assert response.status_code == 401
        assert response.json() == {"detail": "Not authenticated"}

    @pytest.mark.parametrize(
        "params, expected_status",
        [
            ({"offset": "0"}, 200),
            ({"limit": "10"}, 200),
            ({"active": "true"}, 200),
            ({"user_id": 1}, 200),
            ({"views": "true"}, 200),
        ],
    )
    def test_get(self, token, params, expected_status):
        response = self.client.get(
            url="/api/admin/app", params=params, headers={f"Authorization": token}
        )

        assert response.status_code == expected_status

        if expected_status == 200:
            response_data = response.json()

            if "data" in response_data:
                try:
                    app_response = AppsResponse(**response_data)

                    if app_response.data:
                        for item in app_response.data:
                            assert isinstance(item, AppBase)

                except ValidationError as e:
                    pytest.fail(f"Response validation failed: {e}")

        elif expected_status == 422:
            response_data = response.json()
            assert "detail" in response_data
