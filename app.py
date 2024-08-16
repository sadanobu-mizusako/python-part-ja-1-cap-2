from page import UserInputDisplay, SearchResultDisplay, ResultComparison, BookAddOptions
from user_session import UserSession
from domain_context.default_values import DEFAULT_VALUES

user_session = UserSession()
user_session.set_default_values(DEFAULT_VALUES)

UserInputDisplay()
if user_session.user_request_ready():
    SearchResultDisplay()

if user_session.user_choice_ready():
    ResultComparison()
    BookAddOptions()