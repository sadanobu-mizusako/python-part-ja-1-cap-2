import numpy as np
import streamlit as st

from db_manager import SQliteManager
from user_session import UserSession

class DataManage():
    def __init__(self, user_session: UserSession):
        self.state = st.session_state
        self.user_session = user_session
        self._initialize_default_values()

    def _initialize_default_values(self):
        # 必要なセッションステートのデフォルト値を設定
        df_models, df_parts, df_grades = self._load_data_from_DB()
        defaults = {
            "df_models": DataFrame(df_models),
            "df_parts": df_parts,
            "df_grades": df_grades,
            "seach_result": None
        }
        for key, value in defaults.items():
            if key not in self.state:
                self.state[key] = value

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
        df_grades = sql_manager.get_df("""
                                        SELECT BasePrice as price, ImageURL as image_url, ModelName as model_name, CarModels.ModelID as model_id, 
                                        CarGrades.GradeID as grade_id, GradeName as grade_name, Description as grade_desc, Rank as rank, 
                                        FuelEfficiency, FuelCostPerKilo, MonthlyMainteCost, MonthlyInsuranceCost, MonthlyParkingCost, MonthlyPriceDropRate
                                        from CarGrades JOIN Bases ON CarGrades.GradeID == Bases.GradeID
                                        JOIN CarModels ON CarModels.ModelID == CarGrades.ModelID
                                        """)
        # nameだけではユニークにならないので、説明文も追加する
        df_grades["name_desc"] = np.vectorize(lambda name, desc: f"{name} ({desc})")(df_grades["grade_name"], df_grades["grade_desc"])
        
        return df_models, df_parts, df_grades
    
    def calculate_costs(self):
        """
        各種コストを計算するメソッド
        """
        # コストと売却価格
        hold_month = self.user_session.state.age * 12
        self.state.df_grades["FuelCost"] = (self.state.df_grades["FuelCostPerKilo"] * self.user_session.state.hour * 40 * hold_month * 30).astype(int)
        self.state.df_grades["MainteCost"] = (self.state.df_grades["MonthlyMainteCost"] * hold_month).astype(int)
        self.state.df_grades["InsuranceCost"] = (self.state.df_grades["MonthlyMainteCost"] * hold_month).astype(int)
        self.state.df_grades["ResaleValue"] = (self.state.df_grades["price"] * (1-self.state.df_grades["MonthlyPriceDropRate"]) ** (hold_month)).astype(int)
        self.state.df_grades["MonthlyTotalCost"] = self.state.df_grades["FuelCost"]/30 + self.state.df_grades["MonthlyMainteCost"] + self.state.df_grades["MonthlyInsuranceCost"]
        self.state.df_grades["MonthlyRealCost"] = (self.state.df_grades["price"] - self.state.df_grades["ResaleValue"] + self.state.df_grades["MonthlyTotalCost"] + self.state.df_grades["MonthlyTotalCost"] * hold_month)/hold_month
        self.state.df_grades["MonthlyTotalCost"] = self.state.df_grades["MonthlyTotalCost"].astype(int)
        self.state.df_grades["MonthlyRealCost"] = self.state.df_grades["MonthlyRealCost"].astype(int)
    
    def search_car_meet_customer_needs(self):
        """
        ユーザーの要望に合う車両を検索する関数
        入力が正しく、かつデータが存在していればTrueを返す
        検索結果はst.session_state.search_resultへ代入
        """
        target_model_id = self.state["df_models"][self.state["df_models"]['category_name']==self.user_session.state["car_category"]]["model_id"]
        try:
            search_result_df = self.state.df_grades[self.state.df_grades["model_id"].isin(target_model_id)&(self.state.df_grades["MonthlyRealCost"]<int(self.user_session.state['user_budget'])/12)]
            search_result_df = search_result_df.reindex(columns=['image_url', 'model_name', 'name_desc', 'MonthlyRealCost', 'MonthlyTotalCost', 'ResaleValue', 'rank'])
            search_result_df["check"] = False
            self.state.search_result = search_result_df
            return not search_result_df.empty
        except ValueError:
            return None
        
    def get_seach_result(self):
        return self.state.search_result


class DataFrame():
    def __init__(self, df):
        self.df = df

    def get(self):
        return self.df.copy()
    
    def get_single(self, key, value):
        pass

class DataObject():
    def __init__(self, df):
        self.df = df

    def to_db(self):
        pass