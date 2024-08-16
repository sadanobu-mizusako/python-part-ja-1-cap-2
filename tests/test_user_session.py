import pytest
import streamlit as st
from user_session import UserSession

# pytestのフィクスチャを使って、新しいユーザーセッションのインスタンスを作成
@pytest.fixture
def user_session():
    # Streamlitのセッションステートをクリアして初期状態にする
    st.session_state.clear()
    # BaseUserSessionのデフォルト値を設定
    defaults = {
        "car_category": None,
        "user_budget": None,
        "hour": None,
        "age": None,
        "chosen_grades": None
    }
    # UserSessionのインスタンスを作成し、デフォルト値を設定
    session = UserSession()
    session.set_default_values(defaults)
    return session

def test_user_request_ready(user_session):
    # 必要なセッションステートを設定してテスト
    user_session.set_value("car_category", "SUV")
    user_session.set_value("user_budget", "30000")
    user_session.set_value("hour", 10)
    user_session.set_value("age", 25)

    # すべての値が設定されている場合、Trueを返すべき
    assert user_session.user_request_ready() == True

    # いくつかのセッションステートが設定されていない場合、Falseを返すべき
    user_session.set_value("age", None)
    assert user_session.user_request_ready() == False

    # 他のセッションステートが空またはNoneの場合もFalseを返すべき
    user_session.set_value("age", 25)
    user_session.set_value("user_budget", "")
    assert user_session.user_request_ready() == False

def test_user_choice_ready(user_session):
    # 必要なセッションステートを設定してテスト
    user_session.set_value("chosen_grades", ["Grade1", "Grade2"])

    # chosen_gradesがNoneでなく、かつ空でない場合、Trueを返すべき
    assert user_session.user_choice_ready() == True

    # chosen_gradesがNoneの場合、Falseを返すべき
    user_session.set_value("chosen_grades", None)
    assert user_session.user_choice_ready() == False

    # chosen_gradesが空の場合もFalseを返すべき
    user_session.set_value("chosen_grades", [])
    assert user_session.user_choice_ready() == False
