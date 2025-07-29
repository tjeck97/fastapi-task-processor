from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from main import app
from models.task import Task, TaskStatus
from models.conversation import Conversation
from routes import tasks as task_routes

client = TestClient(app)

def mock_task_obj():
    task = Task(id=1, title="Mock Task", status=TaskStatus.pending)
    task.conversations = [
        Conversation(id=1, message="message 1", archived=False),
        Conversation(id=2, message="message 2", archived=False),
    ]
    return task

def test_create_task_route(monkeypatch):
    mock_db = MagicMock()

    def get_db_override():
        yield mock_db

    app.dependency_overrides[task_routes.get_db] = get_db_override

    def refresh(obj):
        obj.id = 1
        obj.status = TaskStatus.pending

    mock_db.add.return_value = None
    mock_db.commit.return_value = None
    mock_db.refresh.side_effect = refresh

    response = client.post("/tasks/", json={"title": "Test Task"})
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Task"
    assert data["status"] == "pending"
    assert data["id"] == 1

def test_list_tasks_route(monkeypatch):
    mock_db = MagicMock()
    mock_db.query().all.return_value = [mock_task_obj()]

    def get_db_override():
        yield mock_db

    app.dependency_overrides[task_routes.get_db] = get_db_override

    response = client.get("/tasks/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert data[0]["title"] == "Mock Task"

def test_create_task_integrity_error(monkeypatch):
    mock_db = MagicMock()
    mock_db.add.side_effect = IntegrityError("Integrity fail", None, None)

    def get_db_override():
        yield mock_db

    app.dependency_overrides[task_routes.get_db] = get_db_override

    response = client.post("/tasks/", json={"title": "Test Task"})
    assert response.status_code == 400
    assert response.json()["detail"] == "Task violates a DB constraint"

def test_create_task_sqlalchemy_error(monkeypatch):
    mock_db = MagicMock()
    mock_db.add.side_effect = SQLAlchemyError("DB error")

    def get_db_override():
        yield mock_db

    app.dependency_overrides[task_routes.get_db] = get_db_override

    response = client.post("/tasks/", json={"title": "Test Task"})
    assert response.status_code == 500
    assert response.json()["detail"] == "Database error while creating task"

def test_create_task_unexpected_exception(monkeypatch):
    mock_db = MagicMock()
    mock_db.add.side_effect = Exception("Unexpected")

    def get_db_override():
        yield mock_db

    app.dependency_overrides[task_routes.get_db] = get_db_override

    response = client.post("/tasks/", json={"title": "Test Task"})
    assert response.status_code == 500
    assert response.json()["detail"] == "Unexpected error while creating task"
