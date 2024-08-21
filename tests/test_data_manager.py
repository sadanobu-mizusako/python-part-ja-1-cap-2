import pytest
import sqlite3
import os
import pandas as pd
import json
from data_manager.data_manager import DataManager, ImmutableDataFrame
from data_manager.base_db_manager import SQliteManager
from domain_context.db_config import CREATE_TABLES_SQL_PATH

# SQLスクリプトのパス
TEST_DB_PATH = 'test_db.sqlite'
DB_MANAGER = SQliteManager(TEST_DB_PATH)


@pytest.fixture(scope="function")
def data_manager():
    # テストDBを作成
    manager = DataManager()
    manager.dbname = TEST_DB_PATH

    # テストDBファイルが存在する場合は削除
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)
    
    # 外部ファイルからSQLスクリプトを読み込む
    with open(CREATE_TABLES_SQL_PATH, 'r', encoding='utf-8') as f:
        create_tables_sql = f.read()
    # テスト用のテーブルを作成
    DB_MANAGER.execute_script(create_tables_sql)
    
    yield manager
    # テストが終わった後にDBファイルを削除
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)

def test_insert_user_customization(data_manager):
    # ユーザーとカスタマイゼーションを挿入
    data_manager.insert_user_customization("John Doe", "john@example.com", "Tokyo", 1, [1], [1], [1,2,3])
    
    # データを取得
    user_data = DB_MANAGER.get_data("SELECT * FROM Users")
    customization_data = DB_MANAGER.get_data("SELECT * FROM Customizations")
    color_customization_data = DB_MANAGER.get_data("SELECT * FROM ColorCustomizations")
    exterior_customization_data = DB_MANAGER.get_data("SELECT * FROM ExteriorCustomizations")
    interior_customization_data = DB_MANAGER.get_data("SELECT * FROM InteriorCustomizations")

    # テスト
    assert len(user_data) == 1
    assert len(customization_data) == 1
    assert len(color_customization_data) == 1
    assert len(exterior_customization_data) == 3
    assert len(interior_customization_data) == 1

    assert user_data[0][1] == "John Doe"
    assert customization_data[0][1] == user_data[0][0]  # user_idが一致することを確認
    assert color_customization_data[0][1] == customization_data[0][0]  # customization_idが一致することを確認
    assert exterior_customization_data[0][1] == customization_data[0][0]  # customization_idが一致することを確認
    assert interior_customization_data[0][1] == customization_data[0][0]  # customization_idが一致することを確認

def test_immutable_dataframe():
    data = {'col1': [1, 2, 3], 'col2': [4, 5, 6]}
    df = pd.DataFrame(data)
    immutable_df = ImmutableDataFrame(df)

    # 元のデータフレームと同じ内容であることを確認
    assert immutable_df['col1'].equals(df['col1'])
    assert immutable_df['col2'].equals(df['col2'])

    # 新しい列の追加が不可能であることを確認
    with pytest.raises(ValueError):
        immutable_df['col3'] = [7, 8, 9]

    # 元の列の変更が不可能であることを確認
    with pytest.raises(ValueError):
        immutable_df['col1'] = [10, 11, 12]

def test_load_data_from_db(data_manager):
    # テスト用のデータを挿入
    DB_MANAGER = SQliteManager(TEST_DB_PATH)
    DB_MANAGER.execute_script("""
    INSERT INTO CarCategories (CategoryName) VALUES ('SUV');
    INSERT INTO CarModels (ModelName, CategoryID, ImageURL) VALUES ('Model X', 1, 'url1');
    INSERT INTO CarGrades (GradeName, Description, ModelID) VALUES ('Grade A', 'Description A', 1);
    INSERT INTO Engines (EngineType) VALUES ('V8');
    INSERT INTO Bases (GradeID, EngineID, BasePrice, Rank, FuelEfficiency, FuelCostPerKilo, MonthlyMainteCost, MonthlyInsuranceCost, MonthlyParkingCost, MonthlyPriceDropRate) 
    VALUES (1, 1, 50000, 1, 15.0, 0.1, 100, 200, 300, 0.05);
    INSERT INTO Colors (ColorName, ImageURL, AdditionalCost) VALUES ('Red', 'color_url', 1000);
    INSERT INTO Exteriors (Item, ImageURL, AdditionalCost) VALUES ('Sunroof', 'exterior_url', 1500);
    INSERT INTO Interiors (Item, ImageURL, AdditionalCost) VALUES ('Leather', 'interior_url', 2000);
    INSERT INTO GradeExteriors (GradeID, ExteriorID) VALUES (1, 1);
    INSERT INTO GradeInteriors (GradeID, InteriorID) VALUES (1, 1);
    """)

    # データをロード
    df_models, df_parts, df_parts_interior, df_colors, df_grades = data_manager.load_data_from_DB()
    print(df_models, df_parts, df_parts_interior, df_colors, df_grades)

    # テスト
    print(df_models)
    assert len(df_models) == 1
    assert df_models.iloc[0]['model_name'] == 'Model X'
    assert len(df_grades) == 1
    assert df_grades.iloc[0]['grade_name'] == 'Grade A'
    assert len(df_parts) == 1
    assert df_parts.iloc[0]['name'] == 'Sunroof'
    assert len(df_parts_interior) == 1
    assert df_parts_interior.iloc[0]['name'] == 'Leather'
    assert len(df_colors) == 1
    assert df_colors.iloc[0]['name'] == 'Red'

def test_icalculate_costs(data_manager):
    data = {
            'price': [10000000, 5000000, 6000000],
            'FuelCostPerKilo': [10, 2, 3],
            'MonthlyMainteCost': [10000, 5000, 6000],
            'MonthlyInsuranceCost': [4000, 5000, 6000],
            'MonthlyPriceDropRate': [0.02, 0.03, 0.01],
            }
    df = pd.DataFrame(data)
    age = 4
    hour = 1
    hold_month = age * 12

    expected_fuel_costs = [10 * 1 * 40 * hold_month * 30, 2 * 1 * 40 * hold_month * 30, 3 * 1 * 40 * hold_month * 30]
    expected_mainte_costs = [10000 * hold_month, 5000 * hold_month, 6000 * hold_month]
    expected_insurance_costs = [4000 * hold_month, 5000 * hold_month, 6000 * hold_month]
    expected_resale_values = [10000000 * (1 - 0.02) ** hold_month, 5000000 * (1 - 0.03) ** hold_month, 6000000 * (1 - 0.01) ** hold_month]

    df = data_manager.calculate_costs(age, hour, df)

    for i in range(len(df)):
        assert df["FuelCost"][i] == expected_fuel_costs[i]
        assert df["MainteCost"][i] == expected_mainte_costs[i]
        assert df["InsuranceCost"][i] == expected_insurance_costs[i]
        assert df["ResaleValue"][i] == int(expected_resale_values[i])
        
        expected_monthly_total_cost = (
            df["FuelCost"][i] / 30 + df["MonthlyMainteCost"][i] + df["MonthlyInsuranceCost"][i]
        )
        assert df["MonthlyTotalCost"][i] == int(expected_monthly_total_cost)
        
        expected_monthly_real_cost = (
            df["price"][i]
            - df["ResaleValue"][i]
            + df["MonthlyTotalCost"][i]
            + df["MonthlyTotalCost"][i] * hold_month
        ) / hold_month
        
        assert df["MonthlyRealCost"][i] == int(expected_monthly_real_cost)
