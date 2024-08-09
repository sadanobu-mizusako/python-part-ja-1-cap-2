from abc import ABC, abstractmethod
import streamlit as st

from user_session import UserSession
from data_manage import DataManage

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
            return edited_df[edited_df["check"]]
        
        else:
            st.write('該当車両がありません')

class DetailResultDisplay(BaseDisplay):
    """
    詳細比較を表示するクラス
    """
    def __init__(self, user_selection) -> None:
        super().__init__()
        self.user_selection = user_selection

    def show(self):
        pass

class ReservationDisplay(BaseDisplay):
    """
    ディーラー予約のクラス
    """
    def user_name(self):
        name = st.text_input("氏名")

    def user_email(self):
        name = st.text_input("メールアドレス")

    def user_prefecture(self):
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

    def send_button(self):
        # フォームの送信ボタン
        if st.button("この内容でディーラーを予約する"):
            st.write("登録が完了しました。後日ディーラーからアポイントのご連絡をいたします。")
            return True
        else:
            return False

    def show(self):
        st.title("ディーラー予約フォーム")      
        st.write("こちらの内容で予約する場合にはフォームを入力・送信してください。")
        self.user_name()
        self.user_email()
        self.user_prefecture()
        st.write("オプションを追加したい方は下からご希望のオプションを選択ください。")
        self.send_button()