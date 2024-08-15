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
        
    def user_choice_ready(self):
        if self.state.chosen_grades != None and len(self.state.chosen_grades)>0:
            return True
        else:
            return False