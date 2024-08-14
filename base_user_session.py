import streamlit as st

class BaseUserSession():
    """
    ユーザーセッションを管理するベースクラス
    """
    def __init__(self, defaults:dict):
        self.state = st.session_state
        self.defaults = defaults
        self._initialize_default_values()

    def _initialize_default_values(self):
        # 必要なセッションステートのデフォルト値を設定
        for key, value in self.defaults.items():
            if key not in self.state:
                self.state[key] = value

    def set_value(self, key, value):
        if key in self.state:
            self.state[key] = value
        else:
            raise KeyError(f"{key} is not a valid key in the session state")

    def set_values(self, values:dict):
        for key in values.keys():
            self.set_value(key, values[key])

    def get_value(self, key):
        if key in self.state:
            return self.state[key]
        else:
            raise KeyError(f"{key} is not a valid key in the session state")
    