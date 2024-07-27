import pandas as pd
import numpy as np
import streamlit as st
import requests
import os

class Customization():
    def __init__(self, option_id, model_id, grade_id):
        user_id = None
        option_id = None
        model_id = model_id
        grade_id = grade_id
        customized_options = {}
    def renuew_options(new_options):
        customized_options = new_options

class CustomizationPage():
    def load_data(self):
        df_models = pd.read_csv("asset/models.csv")
        df_parts = pd.read_csv("asset/exterior_parts.csv")
        df_parts["option_grade_id"] = range(len(df_parts))#ユニークid付与
        df_grades = pd.read_csv("asset/grades.csv")
        # nameだけではユニークにならないので、説明文も追加する
        df_grades["name_desc"] = np.vectorize(lambda name, desc: f"{name} ({desc})")(df_grades["grade_name"], df_grades["desc"])
        
        self.df_models = df_models
        self.df_parts = df_parts
        self.df_grades = df_grades

    def _show_selection(self, df, target_columns, label):
        user_choise = st.selectbox(label=label,options=[""]+df[target_columns].tolist())
        return user_choise

    def _show_data_as_table(self, df, caption_column, image_column, colum_count):
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

    def model_seletion(self):
        st.title("モデル選択")        
        self.target_model = self._show_selection(df=self.df_models, 
                            label="モデルを選択してください", 
                            target_columns="model_name")
        if self.target_model=="":
            self._show_data_as_table(self.df_models, caption_column="model_name", 
                                     image_column="img_url", colum_count=4)
        return self.target_model!=""
    
    def grade_seletion(self):
        st.title("グレード選択")
        self.target_model_id = self.df_models.query("model_name==@self.target_model").model_id.iloc[0]
        self.df_grades_target = self.df_grades.query("model_id==@self.target_model_id")
        st.image(self.df_models.query("model_id==@self.target_model_id").img_url.iloc[0])
        self.target_grade = self._show_selection(df=self.df_grades_target, label="グレードを選択してください", 
                                                 target_columns="name_desc")
        return self.target_grade!=""
    
    def show_total_price(self):
        self.target_model_price = self.df_grades_target.query("name_desc==@self.target_grade").price.iloc[0]
        self.target_model_price = int(self.target_model_price)
        self.header_placeholder = st.empty()# ヘッダーに初期メッセージを表示
        billing_message = f"現在の金額は{self.target_model_price}円です。\n - 基本料金：{self.target_model_price}円"
        self.header_placeholder.write(billing_message)

    def updade_price(self):
        parts_name_list = self.df_parts.query("option_grade_id in @self.target_parts_ids").name.tolist()
        price_list = self.df_parts.query("option_grade_id in @self.target_parts_ids").price.astype(int).tolist()      
        billing_message = f"現在の金額は{self.target_model_price+sum(price_list)}円です。\n - 基本料金：{self.target_model_price}円"
        for name, price in zip(parts_name_list, price_list):
            billing_message += f"\n - {name}: {price}"
        self.header_placeholder.write(billing_message)  

    def user_registration(self):
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
        return st.button("この内容でディーラーを予約する")

    def parts_selection(self):
        st.title("オプション追加") 
        self.target_grade_id = self.df_grades_target.query("name_desc==@self.target_grade").grade_id.iloc[0]
        self.df_parts_target = self.df_parts.query("model_id==@self.target_model_id and grade_id==@self.target_grade_id")
        self.target_parts_ids = self._show_data_as_table_and_select(df=self.df_parts_target, 
                            key_prefix=f"parts_gradeid_{self.target_grade_id}", 
                            caption_column="name", image_column="img_url", 
                            id_column="option_grade_id", colum_count=4)

        return len(self.target_parts_ids)>0

if __name__ == "__main__":
    page = CustomizationPage()

    # データの取得
    page.load_data()

    # モデル選択の誘導
    model_decided = page.model_seletion()

    # グレードの選択の誘導
    if model_decided:
        grade_decided = page.grade_seletion()
    else:
        grade_decided = False

    if grade_decided:
        # ディーラー予約誘導        
        user_registered = page.user_registration()
        # 現在価格の表示
        page.show_total_price()
    else:
        user_registered = False

    # パーツの選択の誘導
    if grade_decided and (user_registered==False):
        parts_decided = page.parts_selection()
    else:
        parts_decided = False
    
    # 価格の更新
    if parts_decided:
        page.updade_price()