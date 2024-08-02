# グレードによって表示するカスタマイズを変更するためサンプルアプリ

import pandas as pd
import numpy as np
import streamlit as st
import requests
import os

from db_manager import SQliteManager

class Customization():
    """
    カスタマイズを管理するクラス。本アプリに統合できていない
    """
    def __init__(self, option_id, model_id, grade_id):
        user_id = None
        option_id = None
        model_id = model_id
        grade_id = grade_id
        customized_options = {}
    def renuew_options(new_options):
        customized_options = new_options

class CustomizationPage():
    """
    ページをコントロールするクラス。機能が複雑化してしまっているので分割して継承させた方がいいかも？以下、分割すべき機能の案：
    - セッション管理
    - 汎用的なビジュアルコンポーネント
    - ページのデザインパーツ（上記との違いはユーザー操作のコンテクストの影響を受けるかどうか）
    - DBマネジメント（ここではpandas.readでcsvからの読み込みのみ実施しているが、将来的にはDBへの読み書きができるように修正する必要）
    """
    def __init__(self):
        """
        各種変数の初期化を実施
        """
        if "customize" not in st.session_state:
            st.session_state.customize = []#カスタマイズ変数の初期化
        if "model_decided" not in st.session_state:
            st.session_state.model_decided = False
        if "grade_decided" not in st.session_state:
            st.session_state.grade_decided = False
        if "user_registered" not in st.session_state:
            st.session_state.user_registered = False
        if "parts_decided" not in st.session_state:
            st.session_state.parts_decided = False

        self.target_grade = None
        self.target_grade_id = None
        self.target_parts_ids = []
        
    def load_data(self):
        """
        とりあえずの処置としてcsvからデータを読み込み
        """
        df_models = pd.read_csv("asset/models.csv")
        df_parts = pd.read_csv("asset/exterior_parts.csv")
        df_parts["option_grade_id"] = range(len(df_parts))#ユニークid付与
        df_grades = pd.read_csv("asset/grades.csv")
        # nameだけではユニークにならないので、説明文も追加する
        df_grades["name_desc"] = np.vectorize(lambda name, desc: f"{name} ({desc})")(df_grades["grade_name"], df_grades["desc"])
        
        self.df_models = df_models
        self.df_parts = df_parts
        self.df_grades = df_grades

    def load_data_from_DB(self):
        """
        DBからデータを読み込み
        """
        sql_manager = SQliteManager("car_customize.db")
        df_models = sql_manager.get_df("SELECT ModelID as model_id, ModelName as model_name, ImageURL as img_url from CarModels")
        df_parts = sql_manager.get_df("""
                                        SELECT Exteriors.ExteriorID as exterior_id, GradeExteriors.GradeID as grade_id, 
                                        ModelID as model_id, Item as name, AdditionalCost as price, ImageURL as img_url 
                                        from Exteriors JOIN GradeExteriors ON Exteriors.ExteriorID == GradeExteriors.ExteriorID
                                        JOIN CarGrades ON GradeExteriors.GradeID == CarGrades.GradeID
                                        """)
        df_parts["option_grade_id"] = range(len(df_parts))#ユニークid付与
        df_grades = sql_manager.get_df("""
                                        SELECT BasePrice as price, ModelID as model_id, CarGrades.GradeID as grade_id, GradeName as grade_name, Description as grade_desc 
                                        from CarGrades JOIN Bases ON CarGrades.GradeID == Bases.GradeID
                                        """)
        # nameだけではユニークにならないので、IDも追加する
        df_grades["name_desc"] = np.vectorize(lambda name, desc: f"{name} ({desc})")(df_grades["grade_name"], df_grades["grade_desc"])
        
        self.df_models = df_models
        self.df_parts = df_parts
        self.df_grades = df_grades

    def _show_selection(self, df, target_columns, label, key):
        """
        リストから1つのオプションを選択するためのビジュアル要素。keyを指定することで、st.session_state[key]から選択肢にアクセスできるようになる
        - df: オプション選択肢を含んだデータフレーム
        - target_columns: 対象となる列名
        - label: ページに表示するラベル
        - key: st.session_stateに保存するための変数名
        """
        user_choise = st.selectbox(label=label,options=[""]+df[target_columns].tolist(), key=key)
        return user_choise

    def _show_data_as_table(self, df, caption_column, image_column, colum_count):
        """
        複数の画像を並べて表示するためのビジュアル要素
        - df: オプション選択肢を含んだデータフレーム
        - caption_column: 画像のキャプションを指定する列名
        - image_column: 画像のURLを指定する列名
        - colum_count: 横何列に並べるかを指定する
        """
        idx = 0
        for _ in range(len(df)-1):
            cols = st.columns(colum_count)
            for i in range(colum_count):
                if idx < len(df):
                    cols[i].image(df[image_column].iloc[idx],width=150, caption=df[caption_column].iloc[idx])
                    idx += 1
                else:
                    break

    def _show_data_as_table_and_select(self, df, key_prefix, caption_column, image_column, id_column, colum_count):
        """
        複数の画像と「チェックボックス」を並べて表示してユーザーに選択させるためのビジュアル要素
        - df: オプション選択肢を含んだデータフレーム
        - key_prefix: keyの前に共通でつけるプレフィックス。各オブジェクトのkeyはkey_prefix_[要素の番号]の形式でsession_stateに保存される
        - caption_column: 画像のキャプションを指定する列名
        - image_column: 画像のURLを指定する列名
        - id_column: 対象を識別するidを指定する列名　#ここでは使用していない。。
        - colum_count: 横何列に並べるかを指定する
        """
        selected_images = []
        image_urls = df[image_column].tolist()
        names = df[caption_column].tolist()
        ids = df[id_column].tolist()
        for i in range(0, len(df), colum_count):
            cols = st.columns(colum_count)
            for j, col in enumerate(cols):
                if i + j < len(image_urls):
                    image_url = image_urls[i + j]
                    name = names[i + j]
                    name = name if len(name)<10 else name[:10]+"..."
                    target_id = ids[i + j]
                    if col.checkbox(name, key=key_prefix+str(i+j)):
                        selected_images.append(target_id)
                    col.image(image_url, caption="", use_column_width=True)
        return selected_images
    
    def _reset_selectbox(self):
        """
        セレクトボックスの値をリセットするためのコールバック関数。保存ボタンを押した後に呼び出すこと想定している
        """
        st.session_state.select_model = ""
        st.session_state.select_grade = ""
        st.session_state.model_decided = False
        st.session_state.grade_decided = False
        st.session_state.parts_decided = False
        customize = {"total_price":self.total_price,
                     "target_model":self.target_model, 
                     "target_grade":self.target_grade, 
                     "target_parts_ids": self.target_parts_ids}
        st.session_state.customize.append(customize)

    def save_customize(self):
        """
        カスタマイズの保存
        """
        st.title("カスタマイズを保存")
        return st.button(label="保存", on_click=self._reset_selectbox) 

    def saved_customize(self):
        """
        保存済みのカスタマイズを表示する
        """
        st.title("保存済みのカスタマイズ")
        self.customization_placeholder = st.empty()
        self.customization_placeholder.write(st.session_state.customize)

    def update_saved_customize(self):
        """
        保存済みのカスタマイズを更新する
        """
        self.customization_placeholder.write(st.session_state.customize)


    def model_seletion(self):
        """
        モデル選択を誘導するページのパーツ
        """
        st.title("モデル選択")        
        self.target_model = self._show_selection(df=self.df_models, 
                            label="モデルを選択してください", 
                            target_columns="model_name", key="select_model")
        if self.target_model=="":
            self._show_data_as_table(self.df_models, caption_column="model_name", 
                                     image_column="img_url", colum_count=4)
        return self.target_model!=""
    
    def grade_seletion(self):
        """
        グレード選択を誘導するページのパーツ
        """
        st.title("グレード選択")
        self.target_model_id = self.df_models.query("model_name==@self.target_model").model_id.iloc[0]
        self.df_grades_target = self.df_grades.query("model_id==@self.target_model_id")
        st.image(self.df_models.query("model_id==@self.target_model_id").img_url.iloc[0])
        self.target_grade = self._show_selection(df=self.df_grades_target, label="グレードを選択してください", 
                                                 target_columns="name_desc", key="select_grade")
        self.target_grade_id = (
            self.df_grades_target.query("name_desc==@self.target_grade").grade_id.iloc[0] 
            if self.target_grade!="" else None
        )
        return self.target_grade!=""
    
    def show_total_price(self):
        """
        合計金額を表示するページのパーツ
        """
        st.title("合計金額")
        self.target_model_price = self.df_grades_target.query("name_desc==@self.target_grade").price.iloc[0]
        self.target_model_price = int(self.target_model_price)
        self.header_placeholder = st.empty()# ヘッダーに初期メッセージを表示。このように定義することで、ページの下部からでも更新をかけることができる
        self.total_price = self.target_model_price
        billing_message = f"現在の金額は{self.target_model_price}円です。\n - 基本料金：{self.target_model_price}円"
        self.header_placeholder.write(billing_message)

    def updade_price(self):
        """
        合計金額を更新する
        """
        parts_name_list = self.df_parts.query("option_grade_id in @self.target_parts_ids").name.tolist()
        price_list = self.df_parts.query("option_grade_id in @self.target_parts_ids").price.astype(int).tolist()
        self.total_price = self.target_model_price+sum(price_list)
        billing_message = f"現在の金額は{self.total_price}円です。\n - 基本料金：{self.target_model_price}円"
        for name, price in zip(parts_name_list, price_list):
            billing_message += f"\n - {name}: {price}"
        self.header_placeholder.write(billing_message)  

    def user_registration(self):
        """
        ユーザー登録用のフォーム
        """
        st.title("ディーラー予約フォーム")        
        st.write("こちらの内容で予約する場合にはフォームを入力・送信してください。")
        st.write("オプションを追加したい方は下からご希望のオプションを選択ください。")
        # ユーザーの氏名の入力
        name = st.text_input("氏名")

        # ユーザーのメールアドレスの入力
        email = st.text_input("メールアドレス")

        # 都道府県の選択
        prefecture = st.selectbox(
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
        if st.button("この内容でディーラーを予約する"):
            st.write("登録が完了しました。後日ディーラーからアポイントのご連絡をいたします。")
            return True
        else:
            return False

    def parts_selection(self):
        """
        オプション選択
        """
        st.title("オプション追加") 
        self.df_parts_target = self.df_parts.query("model_id==@self.target_model_id and grade_id==@self.target_grade_id")
        self.target_parts_ids = self._show_data_as_table_and_select(df=self.df_parts_target, 
                            key_prefix=f"parts_gradeid_{self.target_grade_id}", 
                            caption_column="name", image_column="img_url", 
                            id_column="option_grade_id", colum_count=4)

        return len(self.target_parts_ids)>0

if __name__ == "__main__":
    tab1, tab2 = st.tabs(["モデル選択", "カスタマイズの比較検討・ディーラー予約"])
    page = CustomizationPage()

    # データの取得
    # page.load_data_from_DB()
    page.load_data()

    with tab1:
        if len(st.session_state.customize)>0:
            st.write(f"{len(st.session_state.customize)}件のカスタマイズが保存されています。新しいカスタマイズを作成するか、右のタブで保存したカスタマイズの比較や、ディーラー予約をしましょう。")

        # モデル選択の誘導
        st.session_state.model_decided = page.model_seletion()

        # グレードの選択の誘導
        if st.session_state.model_decided:
            st.session_state.grade_decided = page.grade_seletion()
            
        if st.session_state.grade_decided:
            # 現在価格の表示
            page.show_total_price()

        # セッションにカスタマイズを保存
        if st.session_state.grade_decided:
            st.session_state.customize_saved = page.save_customize()

        # パーツの選択の誘導
        if st.session_state.grade_decided:
            st.session_state.parts_decided = page.parts_selection()
        
        # 価格の更新
        if st.session_state.parts_decided:
            page.updade_price()

    with tab2:
        # 保存済みカスタマイズの表示
        page.saved_customize()
        st.write("ここはきれいに可視化する！！！！")
        # # カスタマイズ表示の更新
        # page.update_saved_customize()
        # ディーラー予約誘導
        st.session_state.user_registered = page.user_registration()