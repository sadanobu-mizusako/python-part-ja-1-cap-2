import streamlit as st
import pandas as pd
import plotly.express as px

from page_manager.base_page import BaseDisplay, UtilityElement
from data_manager.data_manager import DataManager, ImmutableDataFrame
from session_manager.user_session import UserSession

class UserInputDisplay(BaseDisplay, DataManager, UserSession):
    """
    ユーザー要望・使い方を入力してもらう部分のクラス
    """
    def preprocess(self):
        self.init_DB()
        df_models, df_parts, df_parts_interior, df_colors, df_grades = self.load_data_from_DB()
        self.set_values({
            "df_models": ImmutableDataFrame(df_models),
            "df_parts": ImmutableDataFrame(df_parts),
            "df_parts_interior": ImmutableDataFrame(df_parts_interior),
            "df_colors": ImmutableDataFrame(df_colors),
            "df_grades": ImmutableDataFrame(df_grades),
        })

    def postprocess(self):
        self.set_value("car_category", self.car_category)
        self.set_value("user_budget", self.user_budget)
        self.set_value("hour", self.hour)
        self.set_value("age", self.age)

    def show(self):
        """
        個別の入力部分をまとめたメソッド
        """
        st.title("ユーザー要望・使い方 入力")
        self.car_category()
        self.user_budget()
        self.hour()
        self.age()

    def car_category(self):
        """
        カテゴリーの入力部分
        """
        df_models = self.get_value("df_models")
        category_names = df_models["category_name"].drop_duplicates()
        self.car_category = st.selectbox("カテゴリー", category_names, index=None, placeholder="車両カテゴリーを入力ください")

    def user_budget(self):
        """
        年間予算を入力部分
        """
        self.user_budget = st.text_input("予算（円/年）", placeholder = "年間希望予算を入力ください。例:700000")
        if not self._is_number(self.user_budget):
            st.write("※数値を入力して下さい。")

    def hour(self):
        """
        使用時間の入力部分
        """
        self.hour = st.selectbox("1日の乗車時間",(i for i in range(1,24)), index=None, placeholder="1日の乗車時間[H]を入力ください")

    def age(self):
        """
        使用年数の入力部分
        """
        self.age = st.selectbox("使用年数",(i for i in range(1,21)),index=None,placeholder="使用年数を入力ください")
    
    def _is_number(self, value: any):
        """
        値がfloatで変換可能か確認
        """
        try:
            float(value)
            return True
        except ValueError:
            return False

class SearchResultDisplay(BaseDisplay, UserSession):
    """
    検索結果を表示するクラス
    """
    def preprocess(self):
        age = self.get_value("age")
        hour = self.get_value("hour")
        self.calculate_costs(age, hour)
        self.search_car_meet_customer_needs()

    def postprocess(self):
        if self.meets_needs:
            chosen_grades = self.edited_df[self.edited_df["check"]]["name_desc"].tolist()
            self.set_value("chosen_grades",  chosen_grades)

    def show(self):
        """
        検索結果の表示部分
        """
        st.title("検索結果")
        sort_by = "rank" if st.radio(label="並び順", options=("価格順", "人気順"), horizontal=True) == "人気順" else "MonthlyRealCost"
        if self.meets_needs:
            self.edited_df = st.data_editor(
            self.df_search_result.sort_values(by=sort_by).drop(columns=['rank', 'MonthlyRealCost']),
            column_config={
                "image_url": st.column_config.ImageColumn(
                    "image", 
                ),
                "model_name": st.column_config.TextColumn(
                    label="モデル",
                    max_chars=10
                ),
                "MonthlyTotalCost": st.column_config.NumberColumn(
                    label="出費/月",
                ),
                "ResaleValue": st.column_config.NumberColumn(
                    label="売価",
                ),
                "name_desc": st.column_config.TextColumn(
                    label="グレード",
                    width="medium",
                )
            },
            hide_index=True,
            )
        
        else:
            st.write('該当車両がありません')

    def calculate_costs(self, age, hour):
        """
        各種コストを計算するメソッド
        """
        # コストと売却価格
        hold_month = age * 12
        df_grades_with_cost = self.get_value("df_grades").to_dataframe()

        df_grades_with_cost["FuelCost"] = (df_grades_with_cost["FuelCostPerKilo"] * hour * 40 * hold_month * 30).astype(int)
        df_grades_with_cost["MainteCost"] = (df_grades_with_cost["MonthlyMainteCost"] * hold_month).astype(int)
        df_grades_with_cost["InsuranceCost"] = (df_grades_with_cost["MonthlyInsuranceCost"] * hold_month).astype(int)
        df_grades_with_cost["ResaleValue"] = (df_grades_with_cost["price"] * (1-df_grades_with_cost["MonthlyPriceDropRate"]) ** (hold_month)).astype(int)
        df_grades_with_cost["MonthlyTotalCost"] = df_grades_with_cost["FuelCost"]/30 + df_grades_with_cost["MonthlyMainteCost"] + df_grades_with_cost["MonthlyInsuranceCost"]
        df_grades_with_cost["MonthlyRealCost"] = (df_grades_with_cost["price"] - df_grades_with_cost["ResaleValue"] + df_grades_with_cost["MonthlyTotalCost"] + df_grades_with_cost["MonthlyTotalCost"] * hold_month)/hold_month
        df_grades_with_cost["MonthlyTotalCost"] = df_grades_with_cost["MonthlyTotalCost"].astype(int)
        df_grades_with_cost["MonthlyRealCost"] = df_grades_with_cost["MonthlyRealCost"].astype(int)

        self.set_value("df_grades_with_cost", ImmutableDataFrame(df_grades_with_cost))
    
    def search_car_meet_customer_needs(self):
        """
        ユーザーの要望に合う車両を検索する関数
        入力が正しく、かつデータが存在していればTrueを返す
        """
        df_models = self.get_value("df_models")
        car_category = self.get_value("car_category")
        target_model_id = df_models[df_models['category_name']==car_category]["model_id"]
        try:
            df_grades_with_cost = self.get_value("df_grades_with_cost").to_dataframe()
            user_budget = self.get_value("user_budget")
            df_search_result = df_grades_with_cost[df_grades_with_cost["model_id"].isin(target_model_id)&(df_grades_with_cost["MonthlyRealCost"]<int(user_budget)/12)]
            df_search_result = df_search_result.reindex(columns=['image_url', 'model_name', 'name_desc', 'MonthlyRealCost', 'MonthlyTotalCost', 'ResaleValue', 'rank'])
            df_search_result["check"] = False
            self.df_search_result = df_search_result
            self.meets_needs = not(df_search_result.empty)
        except ValueError:
            self.meets_needs = False

class ResultComparison(BaseDisplay, UserSession):
    """
    予約とoption追加をするクラス
    """
    def preprocess(self):
        """
        選択したグレードに対して経過年毎の出費額などを計算する関数
        """
        #### 以下ダミーデータ。今後、ユーザーの選択に応じて、動的に変化させる必要あり
        data1 = {
            '経過年数': [1, 2, 3, 4, 5 , 1, 2, 3, 4, 5],
            'グレード': ['A', 'A', 'A', 'A', 'A', 'B', 'B', 'B', 'B', 'B'],
            '累計出費': [100, 200, 300, 150, 250, 140, 220, 310, 150, 350]
        }

        data2 = {
            '経過年数': [1, 2, 3, 4, 5 , 1, 2, 3, 4, 5],
            'グレード': ['A', 'A', 'A', 'A', 'A', 'B', 'B', 'B', 'B', 'B'],
            '単年出費': [100, 200, 300, 150, 250, 140, 220, 310, 150, 350]
        }

        data3 = {
            'グレード': ['A', 'B', 'A', 'B', 'A', 'B'],
            '費用項目': ['初期費用', '初期費用', 'メンテコスト', 'メンテコスト', '売却益', '売却益'],
            '累計出費': [150, 150, 100, 150, -100, -120]
        }

        self.df1 = pd.DataFrame(data1)
        self.df2 = pd.DataFrame(data2)
        self.df3 = pd.DataFrame(data3)
    
    def postprocess(self):
        pass

    def show(self):
        st.title('ライフサイクルコストの比較')
        st.write("選んだグレードのコストが動的に反映されるようになる予定・・・・")

        col1, col2 = st.columns(2)

        with col1:
            fig1 = px.line(self.df1, x='経過年数', y='累計出費', color='グレード', title='累計出費 vs 経過年数')
            st.plotly_chart(fig1)

            fig3 = px.bar(self.df3, x='グレード', y='累計出費', color='費用項目', title='累計出費 vs 費用項目')
            st.plotly_chart(fig3)

        with col2:
            fig2 = px.bar(self.df2, x='経過年数', y='単年出費', color='グレード', title='単年出費 vs 経過年数', barmode='group')
            st.plotly_chart(fig2)


class BookAddOptions(BaseDisplay, UserSession, DataManager, UtilityElement):
    """
    予約とoption追加をするクラス
    """
    def preprocess(self):
        pass

    def postprocess(self):
        if self.pushed:
            self.insert_user_customization(name=self.name, email=self.email, prefecture=self.prefecture, baseid=self.target_base_id,
                                           exteriorids=self.target_parts_ids, interiorids=self.target_parts_interior_ids,
                                           colorids=self.target_color_ids)

    def show(self):
        st.title("ディーラー予約・オプション追加") 
        col1, col2 = st.columns([2,1])
        img_url = None
        with col1:
            self.target_grade = st.radio(label="ディーラー予約するグレードを選択してください。", options=self.get_value("chosen_grades"))
            df_grades = self.get_value("df_grades")
            self.target_grade_id = df_grades.query("name_desc==@self.target_grade").grade_id.iloc[0]
            self.target_base_id = df_grades.query("name_desc==@self.target_grade").base_id.iloc[0]
            img_url = df_grades.query("name_desc==@self.target_grade").image_url.iloc[0]
        with col2:
            if img_url:
                st.image(img_url)

        st.write("オプション追加を追加する場合は、タブから選択してください。") 
        tab0, tab1, tab2, tab3 = st.tabs(["ディーラー予約", "カラー", "インテリア", "エクステリア"])
        with tab0:
            self.user_registration()
        with tab1:
            self.color_selection()
        with tab2:
            self.parts_interior_selection()
        with tab3:
            self.parts_exterior_selection()


    def user_registration(self):
        """
        ユーザー登録用のフォーム
        """
        st.title("ディーラー予約フォーム")        
        st.write("こちらの内容で予約する場合にはフォームを入力・送信してください。")
        st.write("オプションを追加したい方は下からご希望のオプションを選択ください。")
        # ユーザーの氏名の入力
        self.name = st.text_input("氏名")

        # ユーザーのメールアドレスの入力
        self.email = st.text_input("メールアドレス")

        # 都道府県の選択
        self.prefecture = st.selectbox(
            "都道府県",
            (
                "北海道", "青森県", "岩手県", "宮城県", "秋田県", "山形県", "福島県", "茨城県",
                "栃木県", "群馬県", "埼玉県", "千葉県", "東京都", "神奈川県", "新潟県", "富山県",
                "石川県", "福井県", "山梨県", "長野県", "岐阜県", "静岡県", "愛知県", "三重県",
                "滋賀県", "京都府", "大阪府", "兵庫県", "奈良県", "和歌山県", "鳥取県", "島根県",
                "岡山県", "広島県", "山口県", "徳島県", "香川県", "愛媛県", "高知県", "福岡県",
                "佐賀県", "長崎県", "熊本県", "大分県", "宮崎県", "鹿児島県", "沖縄県"
            )
        )

        # フォームの送信ボタン
        self.pushed = st.button("この内容でディーラーを予約する")
        if self.pushed:
            st.write("登録が完了しました。後日ディーラーからアポイントのご連絡をいたします。")

    def parts_exterior_selection(self):
        df_parts = self.get_value("df_parts")
        self.df_parts_target = df_parts.query("grade_id==@self.target_grade_id")#実質、target_grade_idがuniqueなのでmodelidでのフィルタは解除
        target_parts_ids = self._show_data_as_table_and_select(df=self.df_parts_target, 
                            key_prefix=f"parts_gradeid_{self.target_grade_id}", 
                            caption_column="name", image_column="img_url", 
                            id_column="option_grade_id", colum_count=4)
        self.target_parts_ids = target_parts_ids if target_parts_ids else [None]

    def parts_interior_selection(self):
        df_parts_interior = self.get_value("df_parts_interior")
        self.df_parts_interior_target = df_parts_interior.query("grade_id==@self.target_grade_id")#実質、target_grade_idがuniqueなのでmodelidでのフィルタは解除
        target_parts_interior_ids = self._show_data_as_table_and_select(df=self.df_parts_interior_target, 
                            key_prefix=f"parts_interior_gradeid_{self.target_grade_id}", 
                            caption_column="name", image_column="img_url", 
                            id_column="option_grade_id", colum_count=2)
        self.target_parts_interior_ids = target_parts_interior_ids if target_parts_interior_ids else [None]        

    def color_selection(self):
        self.df_colors_target = self.get_value("df_colors")#実質、target_grade_idがuniqueなのでmodelidでのフィルタは解除
        target_color_ids = self._show_data_as_table_and_select(df=self.df_colors_target, 
                            key_prefix=f"color_gradeid_{self.target_grade_id}", 
                            caption_column="name", image_column="img_url", 
                            id_column="option_grade_id", colum_count=2)
        self.target_color_ids = target_color_ids if target_color_ids else [None]
