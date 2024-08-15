import numpy as np
import streamlit as st
from abc import ABC, abstractmethod
import os
import json

from base_db_manager import SQliteManager, BasicDataObject
from domain_context.env import DB_NAME, CREATE_TABLES_SQL_PATH, DB_JSON_DATA_PATH

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
    """
    ドメインに特化したＤＢとのインタラクションを定義
    """
    sql_manager = SQliteManager(DB_NAME)

    def init_DB(self, dbname=DB_NAME, create_tables_sql_path=CREATE_TABLES_SQL_PATH, db_json_data_path=DB_JSON_DATA_PATH):
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

    def load_data_from_DB(self):
        """
        DBからデータを読み込み
        """
        sql_manager = self.sql_manager
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

    def insert_user_customization(self, name, email, prefecture):
        user_id = BasicDataObject(data={"username":name, "email":email, "place":prefecture}, table_name="Users", db=self.sql_manager).insert_db()
        customization_id = BasicDataObject({"userid":user_id, "baseid":1, "colorid":1, "exteriorid":1, "interiorid":1}, table_name="Customizations", db=self.sql_manager).insert_db()