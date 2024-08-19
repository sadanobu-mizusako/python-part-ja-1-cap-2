from session_manager.base_user_session import BaseUserSession

class UserSession(BaseUserSession):
    """
    本アプリに特化したユーザーセッション管理のクラス
    """
    def user_request_ready(self):
        if self.get_value("car_category") != None and self.get_value("user_budget") != "" \
            and self.get_value("hour") != None and self.get_value("age") != None:
            return True
        else:
            return False
        
    def user_choice_ready(self):
        if self.get_value("chosen_grades") != None and len(self.get_value("chosen_grades"))>0:
            return True
        else:
            return False