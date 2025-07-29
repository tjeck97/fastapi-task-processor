from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from main import app
from models.conversation import Conversation
from routes import conversations as conversation_routes

client = TestClient(app)

def mock_conversation_obj():
    return Conversation(id=1, task_id=1, message="test message", archived=False)

def test_list_conversations(monkeypatch):
    mock_db = MagicMock()
    mock_db.query().filter_by().all.return_value = [mock_conversation_obj()]

    def get_db_override():
        yield mock_db

    app.dependency_overrides[conversation_routes.get_db] = get_db_override

    response = client.get("/conversations/1")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert response.json()[0]["message"] == "test message"

def test_get_all_conversations(monkeypatch):
    mock_db = MagicMock()
    mock_db.query().all.return_value = [mock_conversation_obj()]

    def get_db_override():
        yield mock_db

    app.dependency_overrides[conversation_routes.get_db] = get_db_override

    response = client.get("/conversations/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert response.json()[0]["message"] == "test message"

def test_add_conversation(monkeypatch):
    mock_db = MagicMock()

    def refresh(obj):
        obj.id = 1
        obj.archived = False

    mock_db.add.return_value = None
    mock_db.commit.return_value = None
    mock_db.refresh.side_effect = refresh

    def get_db_override():
        yield mock_db

    app.dependency_overrides[conversation_routes.get_db] = get_db_override

    response = client.post("/conversations/1", params={"message": "hello"})
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "hello"
    assert data["id"] == 1
    assert data["archived"] is False

def test_add_conversation_integrity_error(monkeypatch):
    mock_db = MagicMock()
    mock_db.add.side_effect = IntegrityError("fail", None, None)

    def get_db_override():
        yield mock_db

    app.dependency_overrides[conversation_routes.get_db] = get_db_override

    response = client.post("/conversations/1", params={"message": "hello"})
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid task_id or conversation violates a DB constraint"

def test_add_conversation_sqlalchemy_error(monkeypatch):
    mock_db = MagicMock()
    mock_db.add.side_effect = SQLAlchemyError("fail")

    def get_db_override():
        yield mock_db

    app.dependency_overrides[conversation_routes.get_db] = get_db_override

    response = client.post("/conversations/1", params={"message": "hello"})
    assert response.status_code == 500
    assert response.json()["detail"] == "Unexpected error adding conversation"
