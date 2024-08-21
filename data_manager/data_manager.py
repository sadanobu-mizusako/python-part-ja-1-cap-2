import os
import numpy as np
import json

from data_manager.base_db_manager import SQliteManager
from domain_context.db_config import DB_NAME, CREATE_TABLES_SQL_PATH, DB_JSON_DATA_PATH


class ImmutableDataFrame:
    """
    イミュータブルなデータオブジェクト。最初にインプットした列は変更不可。後から追加した列は変更可
    """

    def __init__(self, df):
        self._original_columns = df.columns
        self._dataframe = df.copy()  # ディープコピーして元データを保護

    def __getitem__(self, key):
        return self._dataframe[key]

    def __setitem__(self, key, value):
        raise ValueError(
            "This DataFrame is immutable. Changes to columns are not allowed."
        )

    def __getattr__(self, attr):
        return getattr(self._dataframe, attr)

    def __repr__(self):
        return repr(self._dataframe)

    def __len__(self):
        return len(self._dataframe)

    def to_dataframe(self):
        return self._dataframe.copy()  # 元データは変更されない


class DataManager:
    """
    ドメインに特化したＤＢとのインタラクションを定義。セキュリティ担保のために参照元から直接クエリを投げる操作を許容しない
    """

    def __init__(self) -> None:
        self.dbname = DB_NAME
        self.create_tables_sql_path = CREATE_TABLES_SQL_PATH
        self.db_json_data_path = DB_JSON_DATA_PATH

    def init_DB(self):
        """
        DBが存在しない場合、jsonファイルからDBを構築する
        """
        _db_manager = SQliteManager(self.dbname)

        if not os.path.isfile(self.dbname):
            with open(self.create_tables_sql_path, "r", encoding="utf-8") as f:
                create_tables_sql = f.read()

            _db_manager.execute_script(create_tables_sql)

            with open(self.db_json_data_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # jsonファイルからデータをDBへ挿入
            _db_manager.insert_data("CarCategories", data["CarCategories"])
            _db_manager.insert_data("CarModels", data["CarModels"])
            _db_manager.insert_data("CarGrades", data["CarGrades"])
            _db_manager.insert_data("Engines", data["Engines"])
            _db_manager.insert_data("Bases", data["Bases"])
            _db_manager.insert_data("Colors", data["Colors"])
            _db_manager.insert_data("Exteriors", data["Exteriors"])
            _db_manager.insert_data("GradeExteriors", data["GradeExteriors"])
            _db_manager.insert_data("Interiors", data["Interiors"])
            _db_manager.insert_data("GradeInteriors", data["GradeInteriors"])

    def load_data_from_DB(self):
        """
        DBからデータを読み込み
        """
        _db_manager = SQliteManager(self.dbname)

        df_models = _db_manager.get_df("""
                                        SELECT ModelID as model_id, CategoryName as category_name, ModelName as model_name, ImageURL as img_url from CarModels
                                        JOIN CarCategories ON CarCategories.CategoryID == CarModels.CategoryID
                                        """)
        df_parts = _db_manager.get_df("""
                                        SELECT Exteriors.ExteriorID as exterior_id, GradeExteriors.GradeID as grade_id, 
                                        ModelID as model_id, Item as name, AdditionalCost as price, ImageURL as img_url 
                                        from Exteriors JOIN GradeExteriors ON Exteriors.ExteriorID == GradeExteriors.ExteriorID
                                        JOIN CarGrades ON GradeExteriors.GradeID == CarGrades.GradeID
                                        """)
        df_parts["option_grade_id"] = range(len(df_parts))  # ユニークid付与
        df_parts_interior = _db_manager.get_df("""
                                        SELECT Interiors.InteriorID as interior_id, GradeInteriors.GradeID as grade_id, 
                                        ModelID as model_id, Item as name, AdditionalCost as price, ImageURL as img_url 
                                        from Interiors JOIN GradeInteriors ON Interiors.InteriorID == GradeInteriors.InteriorID
                                        JOIN CarGrades ON GradeInteriors.GradeID == CarGrades.GradeID
                                        """)
        df_parts_interior["option_grade_id"] = range(
            len(df_parts_interior)
        )  # ユニークid付与
        df_colors = _db_manager.get_df("""
                                        SELECT ColorID as color_id, ColorName as name, AdditionalCost as price, ImageURL as img_url from Colors
                                        """)
        df_colors["option_grade_id"] = range(len(df_colors))  # ユニークid付
        df_grades = _db_manager.get_df("""
                                        SELECT BasePrice as price, ImageURL as image_url, ModelName as model_name, CarModels.ModelID as model_id, 
                                        CarGrades.GradeID as grade_id, GradeName as grade_name, Description as grade_desc, Rank as rank, Bases.BaseId as base_id,
                                        FuelEfficiency, FuelCostPerKilo, MonthlyMainteCost, MonthlyInsuranceCost, MonthlyParkingCost, MonthlyPriceDropRate
                                        from CarGrades JOIN Bases ON CarGrades.GradeID == Bases.GradeID
                                        JOIN CarModels ON CarModels.ModelID == CarGrades.ModelID
                                        """)
        # nameだけではユニークにならないので、説明文も追加する
        df_grades["name_desc"] = np.vectorize(
            lambda model_name, grade_name, desc: f"{model_name} - {grade_name} ({desc})"
        )(df_grades["model_name"], df_grades["grade_name"], df_grades["grade_desc"])
        return df_models, df_parts, df_parts_interior, df_colors, df_grades

    def calculate_costs(self, age, hour, df):
        """
        各種コストを計算するメソッド
        """
        # コストと売却価格
        hold_month = age * 12

        df["FuelCost"] = (df["FuelCostPerKilo"] * hour * 40 * hold_month * 30).astype(
            int
        )
        df["MainteCost"] = (df["MonthlyMainteCost"] * hold_month).astype(int)
        df["InsuranceCost"] = (df["MonthlyInsuranceCost"] * hold_month).astype(int)
        df["ResaleValue"] = (
            df["price"] * (1 - df["MonthlyPriceDropRate"]) ** (hold_month)
        ).astype(int)
        df["MonthlyTotalCost"] = (
            df["FuelCost"] / 30 + df["MonthlyMainteCost"] + df["MonthlyInsuranceCost"]
        )
        df["MonthlyRealCost"] = (
            df["price"]
            - df["ResaleValue"]
            + df["MonthlyTotalCost"]
            + df["MonthlyTotalCost"] * hold_month
        ) / hold_month
        df["MonthlyTotalCost"] = df["MonthlyTotalCost"].astype(int)
        df["MonthlyRealCost"] = df["MonthlyRealCost"].astype(int)

        return df

    def search_car_meet_customer_needs(
        self, df_models, car_category, df_grades_with_cost, user_budget
    ):
        """
        ユーザーの要望に合う車両を検索する関数
        入力が正しく、かつデータが存在していればTrueを返す
        """
        target_model_id = df_models[df_models["category_name"] == car_category][
            "model_id"
        ]
        try:
            df_search_result = df_grades_with_cost[
                df_grades_with_cost["model_id"].isin(target_model_id)
                & (df_grades_with_cost["MonthlyRealCost"] < int(user_budget) / 12)
            ]
            df_search_result = df_search_result.reindex(
                columns=[
                    "image_url",
                    "name_desc",
                    "MonthlyRealCost",
                    "MonthlyTotalCost",
                    "ResaleValue",
                    "rank",
                ]
            )
            df_search_result["check"] = False
            return df_search_result
        except ValueError:
            return None

    def insert_user_customization(
        self, name, email, prefecture, baseid, colorids, interiorids, exteriorids
    ):
        _db_manager = SQliteManager(self.dbname)

        user_id = _db_manager.insert_record(
            "Users", {"username": name, "email": email, "place": prefecture}
        )
        customization_id = _db_manager.insert_record(
            "Customizations",
            {"userid": self._to_int(user_id), "baseid": self._to_int(baseid)},
        )
        for colorid in colorids:
            _db_manager.insert_record(
                "ColorCustomizations",
                {"customizationid": customization_id, "colorid": colorid},
            )
        for interiorid in interiorids:
            _db_manager.insert_record(
                "InteriorCustomizations",
                {"customizationid": customization_id, "interiorid": interiorid},
            )
        for exteriorid in exteriorids:
            _db_manager.insert_record(
                "ExteriorCustomizations",
                {"customizationid": customization_id, "exteriorid": exteriorid},
            )

    def _to_int(self, var):
        if var is not None:
            var = int(var)
        return var
