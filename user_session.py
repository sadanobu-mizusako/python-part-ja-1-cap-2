from base_user_session import BaseUserSession

class UserSession(BaseUserSession):
    """
    本アプリに特化したユーザーセッション管理のクラス
    """
    def user_request_ready(self):
        if self.state["car_category"] != None and self.state["user_budget"] != "" \
            and self.state["hour"] != None and self.state["age"] != None:
            return True
        else:
            return False

# インスタンス化して外部から呼び出せるようにしておく
user_session = UserSession({
        "car_category": None,
        "user_budget": None,
        "hour": None,
        "age": None,
        "tmp_select": None,
        "final_select": None,
        "chosen_grades": None,

        "df_models": None,
        "df_parts": None,
        "df_parts_interior": None,
        "df_colors": None,
        "df_grades": None,
        "df_search_result": None
 })