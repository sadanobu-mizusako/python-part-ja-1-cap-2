from page import UserInputDisplay, SearchResultDisplay, ResultComparison, BookAddOptions
from user_session import UserSession
from data_manage import DataManage

user_session = UserSession()
data_manage = DataManage(user_session)

UserInputDisplay(user_session, data_manage).show()

if user_session.user_request_ready():
    SearchResultDisplay(user_session, data_manage).show()
    ResultComparison(user_session, data_manage).show()
    BookAddOptions(user_session, data_manage).show()
