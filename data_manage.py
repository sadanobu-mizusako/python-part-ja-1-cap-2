import numpy as np
import streamlit as st
from abc import ABC, abstractmethod
import os
import json

from base_db_manager import SQliteManager, BasicDataObject
from user_session import user_session

from env import DB_NAME, CREATE_TABLES_SQL_PATH, DB_JSON_DATA_PATH

class User(BasicDataObject):
    def __init__(self, data: dict):
        super().__init__(data, table_name="Users")

class Customization(BasicDataObject):
    def __init__(self, data: dict):
        super().__init__(data, table_name="Customizations")

class ImmutableDataFrame:
    """
    イミュータブルなデータオブジェクト。最初にインプットした列は変更不可。後から追加した列は変更可
    """
    def __init__(self, df):
        self._original_columns =  df.columns
        self._dataframe = df.copy()  # ディープコピーして元データを保護

    def __getitem__(self, key):
        return self._dataframe[key]

    def __setitem__(self, key, value):
        if key in self._original_columns:
            raise ValueError("This DataFrame is immutable. Changes to existing columns are not allowed.")
        else:
            self._dataframe[key] = value  # 新しい列の追加を許容

    def __getattr__(self, attr):
        return getattr(self._dataframe, attr)

    def __repr__(self):
        return repr(self._dataframe)

    def __len__(self):
        return len(self._dataframe)

    def to_dataframe(self):
        return self._dataframe.copy()  # 元データは変更されない

class DataManage():
    def __init__(self, dbname:str, create_tables_sql_path:str, db_json_data_path:str):
        self._init_DB(dbname, create_tables_sql_path, db_json_data_path)
        self._initialize_default_values()

    def _initialize_default_values(self):
        # 必要なセッションステートのデフォルト値を設定
        df_models, df_parts, df_parts_interior, df_colors, df_grades = self._load_data_from_DB()
        defaults = {
            "df_models": ImmutableDataFrame(df_models),
            "df_parts": ImmutableDataFrame(df_parts),
            "df_parts_interior": ImmutableDataFrame(df_parts_interior),
            "df_colors": ImmutableDataFrame(df_colors),
            "df_grades": ImmutableDataFrame(df_grades),
        }
        user_session.set_values(defaults)

    def _init_DB(self, dbname, create_tables_sql_path, db_json_data_path):
        """
        DBが存在しない場合、jsonファイルからDBを構築する
        """
        if not os.path.isfile(dbname):
            with open(create_tables_sql_path, 'r', encoding='utf-8') as f:
                create_tables_sql = f.read()

            with open(db_json_data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            #DBを作成
            sql_manager = SQliteManager(dbname)
            sql_manager.execute_script(create_tables_sql)

            #jsonファイルからデータをDBへ挿入
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

    def _load_data_from_DB(self):
        """
        DBからデータを読み込み
        """
        sql_manager = SQliteManager("car_customize.db")
        df_models = sql_manager.get_df("""
                                        SELECT ModelID as model_id, CategoryName as category_name, ModelName as model_name, ImageURL as img_url from CarModels
                                        JOIN CarCategories ON CarCategories.CategoryID == CarModels.CategoryID
                                        """)
        df_parts = sql_manager.get_df("""
                                        SELECT Exteriors.ExteriorID as exterior_id, GradeExteriors.GradeID as grade_id, 
                                        ModelID as model_id, Item as name, AdditionalCost as price, ImageURL as img_url 
                                        from Exteriors JOIN GradeExteriors ON Exteriors.ExteriorID == GradeExteriors.ExteriorID
                                        JOIN CarGrades ON GradeExteriors.GradeID == CarGrades.GradeID
                                        """)
        df_parts["option_grade_id"] = range(len(df_parts))#ユニークid付与
        df_parts_interior = sql_manager.get_df("""
                                        SELECT Interiors.InteriorID as interior_id, GradeInteriors.GradeID as grade_id, 
                                        ModelID as model_id, Item as name, AdditionalCost as price, ImageURL as img_url 
                                        from Interiors JOIN GradeInteriors ON Interiors.InteriorID == GradeInteriors.InteriorID
                                        JOIN CarGrades ON GradeInteriors.GradeID == CarGrades.GradeID
                                        """)
        df_parts_interior["option_grade_id"] = range(len(df_parts_interior))#ユニークid付与
        df_colors = sql_manager.get_df("""
                                        SELECT ColorID as color_id, ColorName as name, AdditionalCost as price, ImageURL as img_url from Colors
                                        """)
        df_colors["option_grade_id"] = range(len(df_colors))#ユニークid付        
        df_grades = sql_manager.get_df("""
                                        SELECT BasePrice as price, ImageURL as image_url, ModelName as model_name, CarModels.ModelID as model_id, 
                                        CarGrades.GradeID as grade_id, GradeName as grade_name, Description as grade_desc, Rank as rank, 
                                        FuelEfficiency, FuelCostPerKilo, MonthlyMainteCost, MonthlyInsuranceCost, MonthlyParkingCost, MonthlyPriceDropRate
                                        from CarGrades JOIN Bases ON CarGrades.GradeID == Bases.GradeID
                                        JOIN CarModels ON CarModels.ModelID == CarGrades.ModelID
                                        """)
        # nameだけではユニークにならないので、説明文も追加する
        df_grades["name_desc"] = np.vectorize(lambda name, desc: f"{name} ({desc})")(df_grades["grade_name"], df_grades["grade_desc"])
        
        return df_models, df_parts, df_parts_interior, df_colors, df_grades
    
    def calculate_costs(self):
        """
        各種コストを計算するメソッド
        """
        # コストと売却価格
        hold_month = user_session.state.age * 12
        user_session.state.df_grades["FuelCost"] = (user_session.state.df_grades["FuelCostPerKilo"] * user_session.state.hour * 40 * hold_month * 30).astype(int)
        user_session.state.df_grades["MainteCost"] = (user_session.state.df_grades["MonthlyMainteCost"] * hold_month).astype(int)
        user_session.state.df_grades["InsuranceCost"] = (user_session.state.df_grades["MonthlyMainteCost"] * hold_month).astype(int)
        user_session.state.df_grades["ResaleValue"] = (user_session.state.df_grades["price"] * (1-user_session.state.df_grades["MonthlyPriceDropRate"]) ** (hold_month)).astype(int)
        user_session.state.df_grades["MonthlyTotalCost"] = user_session.state.df_grades["FuelCost"]/30 + user_session.state.df_grades["MonthlyMainteCost"] + user_session.state.df_grades["MonthlyInsuranceCost"]
        user_session.state.df_grades["MonthlyRealCost"] = (user_session.state.df_grades["price"] - user_session.state.df_grades["ResaleValue"] + user_session.state.df_grades["MonthlyTotalCost"] + user_session.state.df_grades["MonthlyTotalCost"] * hold_month)/hold_month
        user_session.state.df_grades["MonthlyTotalCost"] = user_session.state.df_grades["MonthlyTotalCost"].astype(int)
        user_session.state.df_grades["MonthlyRealCost"] = user_session.state.df_grades["MonthlyRealCost"].astype(int)
    
    def search_car_meet_customer_needs(self):
        """
        ユーザーの要望に合う車両を検索する関数
        入力が正しく、かつデータが存在していればTrueを返す
        検索結果はst.session_state.search_resultへ代入
        """
        target_model_id = user_session.state["df_models"][user_session.state["df_models"]['category_name']==user_session.state["car_category"]]["model_id"]
        try:
            df_search_result = user_session.state.df_grades[user_session.state.df_grades["model_id"].isin(target_model_id)&(user_session.state.df_grades["MonthlyRealCost"]<int(user_session.state['user_budget'])/12)]
            df_search_result = df_search_result.reindex(columns=['image_url', 'model_name', 'name_desc', 'MonthlyRealCost', 'MonthlyTotalCost', 'ResaleValue', 'rank'])
            df_search_result["check"] = False
            user_session.state.df_search_result = df_search_result
            return not df_search_result.empty
        except ValueError:
            return None
        
    def get_seach_result(self):
        return user_session.state.df_search_result.copy()

data_manage = DataManage(DB_NAME, 
                         CREATE_TABLES_SQL_PATH, 
                         DB_JSON_DATA_PATH)