import streamlit as st

class UserSession():
    def __init__(self):
        self.state = st.session_state
        self._initialize_default_values()

    def _initialize_default_values(self):
        # 必要なセッションステートのデフォルト値を設定
        defaults = {
            "car_category": None,
            "user_budget": None,
            "hour": None,
            "age": None,
            "tmp_select": None,
            "final_select": None,
        }
        for key, value in defaults.items():
            if key not in self.state:
                self.state[key] = value

    def set_value(self, key, value):
        if key in self.state:
            self.state[key] = value
        else:
            raise KeyError(f"{key} is not a valid key in the session state")

    def get_value(self, key):
        if key in self.state:
            return self.state[key]
        else:
            raise KeyError(f"{key} is not a valid key in the session state")
        
    def user_request_ready(self):
        if self.state["car_category"] != None and self.state["user_budget"] != "" \
            and self.state["hour"] != None and self.state["age"] != None:
            return True
        else:
            return False
