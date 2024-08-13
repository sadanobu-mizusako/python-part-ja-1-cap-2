from abc import ABC, abstractmethod
import sqlite3
import json
import pandas as pd

class DBManagerBase(ABC):
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

class SQliteManager(DBManagerBase):
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

if __name__ == "__main__":

    create_tables_sql = """
CREATE TABLE CarCategories (
    CategoryID INTEGER PRIMARY KEY AUTOINCREMENT,
    CategoryName TEXT
);

CREATE TABLE CarModels (
    ModelID INTEGER PRIMARY KEY AUTOINCREMENT,
    ModelName TEXT,
    CategoryID INTEGER,
    ImageURL TEXT,
    FOREIGN KEY (CategoryID) REFERENCES CarCategories (CategoryID)
);

CREATE TABLE CarGrades (
    GradeID INTEGER PRIMARY KEY AUTOINCREMENT,
    GradeName TEXT,
    Description TEXT,
    ModelID INTEGER,
    FOREIGN KEY (ModelID) REFERENCES CarModels (ModelID)
);

CREATE TABLE Engines (
    EngineID INTEGER PRIMARY KEY AUTOINCREMENT,
    EngineType TEXT
);

CREATE TABLE Bases (
    BaseID INTEGER PRIMARY KEY AUTOINCREMENT,
    GradeID INTEGER,
    EngineID INTEGER,
    BasePrice INTEGER,
    Rank INTEGER,
    FuelEfficiency REAL,
    FuelCostPerKilo REAL,
    MonthlyMainteCost REAL,
    MonthlyInsuranceCost REAL,
    MonthlyParkingCost REAL,
    MonthlyPriceDropRate REAL,
    FOREIGN KEY (GradeID) REFERENCES CarGrades (GradeID),
    FOREIGN KEY (EngineID) REFERENCES Engines (EngineID)
);

CREATE TABLE Colors (
    ColorID INTEGER PRIMARY KEY AUTOINCREMENT,
    ColorName TEXT,
    ImageURL TEXT,
    AdditionalCost INTEGER
);

CREATE TABLE Exteriors (
    ExteriorID INTEGER PRIMARY KEY AUTOINCREMENT,
    Item TEXT,
    ImageURL TEXT,
    AdditionalCost INTEGER
);

CREATE TABLE GradeExteriors (
    GradeExteriorID INTEGER PRIMARY KEY AUTOINCREMENT,
    GradeID INTEGER,
    ExteriorID INTEGER,
    FOREIGN KEY (GradeID) REFERENCES CarGrades (GradeID),
    FOREIGN KEY (ExteriorID) REFERENCES Exteriors (ExteriorID)
);

CREATE TABLE Interiors (
    InteriorID INTEGER PRIMARY KEY AUTOINCREMENT,
    Item TEXT,
    ImageURL TEXT,
    AdditionalCost INTEGER
);

CREATE TABLE GradeInteriors (
    GradeInteriorID INTEGER PRIMARY KEY AUTOINCREMENT,
    GradeID INTEGER,
    InteriorID INTEGER,
    FOREIGN KEY (GradeID) REFERENCES CarGrades (GradeID),
    FOREIGN KEY (InteriorID) REFERENCES Interiors (InteriorID)
);

CREATE TABLE Customizations (
    CustomizationID INTEGER PRIMARY KEY AUTOINCREMENT,
    UserID INTEGER,
    BaseID INTEGER,
    ColorID INTEGER,
    ExteriorID INTEGER,
    InteriorID INTEGER,
    FOREIGN KEY (UserID) REFERENCES Users (UserID),
    FOREIGN KEY (BaseID) REFERENCES Bases (BaseID),
    FOREIGN KEY (ColorID) REFERENCES Colors (ColorID),
    FOREIGN KEY (ExteriorID) REFERENCES Exteriors (ExteriorID),
    FOREIGN KEY (InteriorID) REFERENCES Interiors (InteriorID)
);

CREATE TABLE Users (
    UserID INTEGER PRIMARY KEY AUTOINCREMENT,
    UserName TEXT,
    Email TEXT,
    Place TEXT
);
"""
    def load_json(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)

    #DBを作成
    sql_manager = SQliteManager("car_customize.db")
    sql_manager.execute_script(create_tables_sql)

    #jsonファイルからデータをDBへ挿入
    data = load_json("db_sample.json")
    sql_manager.insert_data('CarCategories', data['CarCategories'])
    sql_manager.insert_data('CarModels', data['CarModels'])
    sql_manager.insert_data('CarGrades', data['CarGrades'])
    sql_manager.insert_data('Engines', data['Engines'])
    sql_manager.insert_data('Bases', data['Bases'])
    sql_manager.insert_data('Colors', data['Colors'])
    sql_manager.insert_data('Exteriors', data['Exteriors'])
    sql_manager.insert_data('GradeExteriors', data['GradeExteriors'])
    sql_manager.insert_data('Interiors', data['Interiors'])
    sql_manager.insert_data('GradeInteriors', data['GradeInteriors'])
    # sql_manager.insert_data('Customizations', data['Customizations'])
    # sql_manager.insert_data('Users', data['Users'])