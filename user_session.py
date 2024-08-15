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