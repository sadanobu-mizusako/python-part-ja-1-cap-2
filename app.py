from page import UserInputDisplay, SearchResultDisplay, DetailResultDisplay, ReservationDisplay
from user_session import UserSession
from data_manage import DataManage

user_session = UserSession()
data_manage = DataManage(user_session)

user_input_display = UserInputDisplay(user_session, data_manage)
user_input_display.show()
if user_session.user_request_ready():
    search_result_display = SearchResultDisplay(user_session, data_manage)
    search_result_display.show()

reservation_display = ReservationDisplay(user_session, data_manage)
reservation_display.show()
