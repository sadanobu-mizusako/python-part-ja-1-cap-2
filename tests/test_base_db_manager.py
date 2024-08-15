import pytest
import sqlite3
import os
from base_db_manager import SQliteManager, BasicDataObject

# テスト用のSQLiteデータベースファイルのパス
TEST_DB_PATH = 'test_db.sqlite'

@pytest.fixture(scope="function")
def db_manager():
    # テストDBを作成
    manager = SQliteManager(TEST_DB_PATH)
    yield manager
    # テストが終わった後にDBファイルを削除
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)

@pytest.fixture(scope="function")
def setup_db(db_manager):
    # テスト用のテーブルを作成
    db_manager.execute_script("""
    CREATE TABLE test_table (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        age INTEGER NOT NULL
    );
    """)
    yield
    db_manager.execute_script("DROP TABLE test_table;")

def test_insert_data(db_manager, setup_db):
    data = [
        {"name": "Alice", "age": 30},
        {"name": "Bob", "age": 25}
    ]
    db_manager.insert_data("test_table", data)
    
    result = db_manager.get_data("SELECT * FROM test_table")
    assert len(result) == 2
    assert result[0][1] == "Alice"
    assert result[0][2] == 30
    assert result[1][1] == "Bob"
    assert result[1][2] == 25

def test_insert_record(db_manager, setup_db):
    record = {"name": "Charlie", "age": 35}
    last_id = db_manager.insert_record("test_table", record)
    
    result = db_manager.get_data(f"SELECT * FROM test_table WHERE id = {last_id}")
    assert len(result) == 1
    assert result[0][1] == "Charlie"
    assert result[0][2] == 35

def test_get_data(db_manager, setup_db):
    data = [
        {"name": "Alice", "age": 30},
        {"name": "Bob", "age": 25}
    ]
    db_manager.insert_data("test_table", data)
    
    result = db_manager.get_data("SELECT * FROM test_table")
    assert len(result) == 2
    assert result[0][1] == "Alice"
    assert result[0][2] == 30
    assert result[1][1] == "Bob"
    assert result[1][2] == 25

def test_get_df(db_manager, setup_db):
    data = [
        {"name": "Alice", "age": 30},
        {"name": "Bob", "age": 25}
    ]
    db_manager.insert_data("test_table", data)
    
    df = db_manager.get_df("SELECT * FROM test_table")
    assert df is not None
    assert len(df) == 2
    assert df.iloc[0]['name'] == "Alice"
    assert df.iloc[0]['age'] == 30
    assert df.iloc[1]['name'] == "Bob"
    assert df.iloc[1]['age'] == 25

def test_basic_data_object_insert_db(db_manager, setup_db):
    data = {"name": "David", "age": 40}
    data_object = BasicDataObject(data, "test_table", db_manager)
    last_id = data_object.insert_db()
    
    result = db_manager.get_data(f"SELECT * FROM test_table WHERE id = {last_id}")
    assert len(result) == 1
    assert result[0][1] == "David"
    assert result[0][2] == 40
