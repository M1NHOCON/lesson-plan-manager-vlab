import pytest

from app import create_app
from app.database import db


@pytest.fixture()
def app(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "mock")
    monkeypatch.setenv("LLM_API_KEY", "your_api_key_here")
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    app = create_app(
        test_config={
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "SQLALCHEMY_TRACK_MODIFICATIONS": False,
            "LLM_PROVIDER": "mock",
            "LLM_API_KEY": "your_api_key_here",
        }
    )

    with app.app_context():
        db.drop_all()
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()
        db.engine.dispose()


@pytest.fixture()
def client(app):
    return app.test_client()
