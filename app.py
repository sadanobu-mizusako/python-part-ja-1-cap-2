from page import BaseDisplay, UserInputDisplay, SearchResultDisplay, ResultComparison, BookAddOptions
from user_session import UserSession
from data_manage import DataManage
from default_values import DEFAULT_VALUES

user_session = UserSession()
user_session.set_default(DEFAULT_VALUES)

UserInputDisplay()
if user_session.user_request_ready():
    SearchResultDisplay()
    ResultComparison()
    BookAddOptions()
