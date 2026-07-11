from backend.app.database.init_db import init_db


def test_database_initialization_creates_schema():
    init_db()
