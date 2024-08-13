from abc import ABC, abstractmethod
import streamlit as st
import pandas as pd
import plotly.express as px

from user_session import UserSession
from data_manage import DataManage, User, Customization


class BaseDisplay(ABC):
    def __init__(self, user_session: UserSession, data_manage: DataManage) -> None:
        self.user_session = user_session
        self.data_manage = data_manage

    @abstractmethod
    def show():
        pass

class UserInputDisplay(BaseDisplay):
    """
    ユーザー要望・使い方を入力してもらう部分のクラス
    """
    def car_category(self):
        """
        カテゴリーの入力部分
        """
        self.user_session.set_value("car_category", 
                                    st.selectbox("カテゴリー", self.data_manage.state["df_models"]["category_name"].drop_duplicates(),
                                                index=None, placeholder="車両カテゴリーを入力ください"))

    def user_budget(self):
        """
        年間予算を入力部分
        """
        self.user_session.set_value("user_budget",
                                    st.text_input("予算（円/年）", placeholder = "年間希望予算を入力ください。例:700000"))
        if not self._is_number(self.user_session.get_value("user_budget")):
            st.write("※数値を入力して下さい。")


    def hour(self):
        """
        使用時間の入力部分
        """
        self.user_session.set_value("hour",
                                    st.selectbox("1日の乗車時間",(i for i in range(1,24)), index=None, placeholder="1日の乗車時間[H]を入力ください"))

    def age(self):
        """
        使用年数の入力部分
        """
        self.user_session.set_value("age",
                                    st.selectbox("使用年数",(i for i in range(1,21)),index=None,placeholder="使用年数を入力ください"))

    def show(self):
        """
        個別の入力部分をまとめたメソッド
        """
        st.title("ユーザー要望・使い方 入力")
        self.car_category()
        self.user_budget()
        self.hour()
        self.age()

    def _is_number(self, value: any):
        """
        値がfloatで変換可能か確認
        """
        try:
            float(value)
            return True
        except ValueError:
            return False

class SearchResultDisplay(BaseDisplay):
    """
    検索結果を表示するクラス
    """
    def __init__(self, user_session: UserSession, data_manage: DataManage) -> None:
        super().__init__(user_session, data_manage)
        self.data_manage.calculate_costs()

    def show(self):
        """
        検索結果の表示部分
        """
        st.title("検索結果")
        sort_by = "rank" if st.radio(label="並び順", options=("価格順", "人気順"), horizontal=True) == "人気順" else "MonthlyRealCost"
        if self.data_manage.search_car_meet_customer_needs():
            edited_df = st.data_editor(
            self.data_manage.get_seach_result().sort_values(by=sort_by).drop(columns=['rank', 'MonthlyRealCost']),
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
            self.user_session.set_value("chosen_grades",  edited_df[edited_df["check"]]["name_desc"].tolist())
        
        else:
            st.write('該当車両がありません')

class ResultComparison(BaseDisplay):
    """
    予約とoption追加をするクラス
    """
    def __init__(self, user_session: UserSession, data_manage: DataManage) -> None:
        super().__init__(user_session, data_manage)
    
    def _create_data_frame_for_grade_comparison(self):
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

        df1 = pd.DataFrame(data1)
        df2 = pd.DataFrame(data2)
        df3 = pd.DataFrame(data3)
        return df1, df2, df3

    def show(self):
        df1, df2, df3 = self._create_data_frame_for_grade_comparison()
        st.title('ライフサイクルコストの比較')
        st.write("選んだグレードのコストが動的に反映されるようになる予定・・・・")

        col1, col2 = st.columns(2)

        with col1:
            fig1 = px.line(df1, x='経過年数', y='累計出費', color='グレード', title='累計出費 vs 経過年数')
            st.plotly_chart(fig1)

            fig3 = px.bar(df3, x='グレード', y='累計出費', color='費用項目', title='累計出費 vs 費用項目')
            st.plotly_chart(fig3)

        with col2:
            fig2 = px.bar(df2, x='経過年数', y='単年出費', color='グレード', title='単年出費 vs 経過年数', barmode='group')
            st.plotly_chart(fig2)


class BookAddOptions(BaseDisplay):
    """
    予約とoption追加をするクラス
    """
    def __init__(self, user_session: UserSession, data_manage: DataManage) -> None:
        super().__init__(user_session, data_manage)

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
            user_id = User({"username":name, "email":email, "place":prefecture}).insert_db()
            customization_id = Customization({"userid":user_id, "baseid":1, "colorid":1, "exteriorid":1, "interiorid":1}).insert_db()
            return True
        else:
            return False

    def parts_exterior_selection(self):
        df_parts = self.data_manage.state["df_parts"]
        self.df_parts_target = df_parts.query("grade_id==@self.target_grade_id")#実質、target_grade_idがuniqueなのでmodelidでのフィルタは解除
        self.target_parts_ids = self._show_data_as_table_and_select(df=self.df_parts_target, 
                            key_prefix=f"parts_gradeid_{self.target_grade_id}", 
                            caption_column="name", image_column="img_url", 
                            id_column="option_grade_id", colum_count=4)
        
    def parts_interior_selection(self):
        df_parts_interior = self.data_manage.state["df_parts_interior"]
        self.df_parts_interior_target = df_parts_interior.query("grade_id==@self.target_grade_id")#実質、target_grade_idがuniqueなのでmodelidでのフィルタは解除
        self.target_parts_interior_ids = self._show_data_as_table_and_select(df=self.df_parts_interior_target, 
                            key_prefix=f"parts_interior_gradeid_{self.target_grade_id}", 
                            caption_column="name", image_column="img_url", 
                            id_column="option_grade_id", colum_count=2)

    def color_selection(self):
        self.df_colors_target = self.data_manage.state["df_colors"]#実質、target_grade_idがuniqueなのでmodelidでのフィルタは解除
        self.target_parts_ids = self._show_data_as_table_and_select(df=self.df_colors_target, 
                            key_prefix=f"color_gradeid_{self.target_grade_id}", 
                            caption_column="name", image_column="img_url", 
                            id_column="option_grade_id", colum_count=2)

    def show(self):
        st.title("ディーラー予約・オプション追加") 
        col1, col2 = st.columns([2,1])
        img_url = None
        with col1:
            self.target_grade = st.radio(label="ディーラー予約するグレードを選択してください。", options=self.user_session.get_value("chosen_grades"))

            df_grades = self.data_manage.state["df_grades"]
            self.target_grade_id = df_grades.query("name_desc==@self.target_grade").grade_id.iloc[0]
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
