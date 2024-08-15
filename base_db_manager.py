from abc import ABC, abstractmethod
import sqlite3
import json
import pandas as pd

class BaseDBManager(ABC):
    def __init__(self, path: str) -> None:
        self.path = path

    @abstractmethod
    def execute_script():
        pass

    @abstractmethod
    def execute_many():
        pass

    @abstractmethod
    def insert_data(self, data):
        pass

class SQliteManager(BaseDBManager):
    def execute(self, sql: str):
        conn = sqlite3.connect(self.path)
        cursor = conn.cursor()
        cursor.execute(sql)
        conn.commit()
        conn.close()

    def execute_script(self, sql: str):
        conn = sqlite3.connect(self.path)
        cursor = conn.cursor()
        cursor.executescript(sql)
        conn.commit()
        conn.close()

    def execute_many(self, sql: str, value: list):
        conn = sqlite3.connect(self.path)
        cursor = conn.cursor()
        cursor.executemany(sql, value)
        conn.commit()
        conn.close()

    def insert_data(self, table, data):
        keys = data[0].keys()
        columns = ', '.join(keys)
        placeholders = ', '.join(['?'] * len(keys))
        values = [tuple(item[key] for key in keys) for item in data]
        self.execute_many(f"INSERT INTO {table} ({columns}) VALUES ({placeholders})", values)

    def insert_record(self, table, record)-> int: 
        conn = sqlite3.connect(self.path)
        cursor = conn.cursor()
        print(record)
        keys = record.keys()
        columns = ', '.join(keys)
        placeholders = ', '.join(['?'] * len(keys))
        values = tuple(record[key] for key in keys)
        cursor.execute(f"INSERT INTO {table} ({columns}) VALUES ({placeholders})", values)
        last_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return last_id

    def get_data(self, sql: str) -> tuple:
        conn = sqlite3.connect(self.path)
        cursor = conn.cursor()
        cursor.execute(sql)
        data = cursor.fetchall()
        conn.commit()
        conn.close()
        return data
    
    def get_df(self, sql: str) -> pd.DataFrame|None:
        try:
            conn = sqlite3.connect(self.path)
            df = pd.read_sql_query(sql, conn)
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
            df = None
        finally:
            conn.close()
        return df

class BasicDataObject(ABC):
    def __init__(self, data:dict, table_name:str, db:BaseDBManager):
        self.data = data
        self.table_name = table_name
        self.db = db

    def insert_db(self) -> int:
        """
        DBにデータをインサートしてIDを取得する
        """
        return self.db.insert_record(self.table_name, self.data)