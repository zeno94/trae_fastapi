from datetime import datetime

import pytest
from starlette.testclient import TestClient

from main import GreetResponse


class TestRootEndpoint:
    """测试根路径 GET /"""

    def test_root_returns_welcome_message(self, client: TestClient):
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Welcome to Greeting Service"
        assert data["docs"] == "/docs"


class TestHealthEndpoint:
    """测试健康检查 GET /health"""

    def test_health_returns_ok(self, client: TestClient):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


class TestGreetEndpoint:
    """测试问候接口 GET /greet/{name}"""

    def test_greet_morning(self, client: TestClient, monkeypatch):
        """验证 6:00~17:59 返回「早安」问候语。"""

        class MorningDatetime:
            @classmethod
            def now(cls):
                return datetime(2026, 5, 16, 10, 0, 0, 0)

        monkeypatch.setattr("main.datetime", MorningDatetime)
        response = client.get("/greet/Alice")
        assert response.status_code == 200
        data = response.json()
        assert "早安" in data["message"]
        assert "Alice" in data["message"]

    def test_greet_evening(self, client: TestClient, monkeypatch):
        """验证 18:00~5:59 返回「晚安」问候语。"""

        class EveningDatetime:
            @classmethod
            def now(cls):
                return datetime(2026, 5, 16, 22, 0, 0, 0)

        monkeypatch.setattr("main.datetime", EveningDatetime)
        response = client.get("/greet/Bob")
        assert response.status_code == 200
        data = response.json()
        assert "晚安" in data["message"]
        assert "Bob" in data["message"]

    def test_greet_edge_dawn(self, client: TestClient, monkeypatch):
        """边界：5:59 应判定为晚间，返回「晚安」。"""

        class EdgeDawn:
            @classmethod
            def now(cls):
                return datetime(2026, 5, 16, 5, 59, 0, 0)

        monkeypatch.setattr("main.datetime", EdgeDawn)
        response = client.get("/greet/Eve")
        assert response.status_code == 200
        assert "晚安" in response.json()["message"]

    def test_greet_edge_morning_start(self, client: TestClient, monkeypatch):
        """边界：6:00 应判定为早晨，返回「早安」。"""

        class EdgeMorning:
            @classmethod
            def now(cls):
                return datetime(2026, 5, 16, 6, 0, 0, 0)

        monkeypatch.setattr("main.datetime", EdgeMorning)
        response = client.get("/greet/Eve")
        assert response.status_code == 200
        assert "早安" in response.json()["message"]

    def test_greet_edge_evening_start(self, client: TestClient, monkeypatch):
        """边界：18:00 应判定为晚间，返回「晚安」。"""

        class EdgeEvening:
            @classmethod
            def now(cls):
                return datetime(2026, 5, 16, 18, 0, 0, 0)

        monkeypatch.setattr("main.datetime", EdgeEvening)
        response = client.get("/greet/Eve")
        assert response.status_code == 200
        assert "晚安" in response.json()["message"]

    @pytest.mark.parametrize(
        "name",
        [
            "中文名",
            "John_Doe",
            "user123",
            "a",
        ],
    )
    def test_greet_various_names(self, client: TestClient, name):
        """参数化测试：不同格式的名称均能正常处理。"""
        response = client.get(f"/greet/{name}")
        assert response.status_code == 200
        data = response.json()
        assert name in data["message"]
        assert "message" in data
        assert "timestamp" in data

    def test_greet_url_encoded_name(self, client: TestClient):
        """测试 URL 编码的特殊字符名称。"""
        response = client.get("/greet/%E4%B8%96%E7%95%8C")
        assert response.status_code == 200
        assert "世界" in response.json()["message"]

    def test_greet_response_model_structure(self, client: TestClient):
        """验证响应体结构与 GreetResponse 模型一致。"""
        response = client.get("/greet/Test")
        assert response.status_code == 200
        data = response.json()
        assert list(data.keys()) == ["message", "timestamp"]
        assert isinstance(data["message"], str)
        assert isinstance(data["timestamp"], str)


class TestGreetResponseModel:
    """测试 Pydantic 模型 GreetResponse"""

    def test_model_valid_data(self):
        obj = GreetResponse(message="早安，World", timestamp="2026-05-16T10:00:00")
        assert obj.message == "早安，World"
        assert obj.timestamp == "2026-05-16T10:00:00"

    def test_model_serialization(self):
        obj = GreetResponse(message="早安，World", timestamp="2026-05-16T10:00:00")
        serialized = obj.model_dump()
        assert serialized == {"message": "早安，World", "timestamp": "2026-05-16T10:00:00"}
