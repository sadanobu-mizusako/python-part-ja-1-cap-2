from page import UserInputDisplay, SearchResultDisplay, ResultComparison, BookAddOptions
from user_session import user_session

UserInputDisplay()

if user_session.user_request_ready():
    SearchResultDisplay()
    ResultComparison()
    BookAddOptions()
