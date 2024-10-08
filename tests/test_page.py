import pytest
import streamlit as st
from page_manager.page import UserInputDisplay, SearchResultDisplay, ResultComparison
from session_manager.user_session import UserSession
from data_manager.data_manager import ImmutableDataFrame
import pandas as pd


@pytest.fixture(scope="function")
def user_session():
    # Streamlitのセッションステートをクリアして初期状態にする
    st.session_state.clear()
    # BaseUserSessionのデフォルト値を設定
    defaults = {
        "car_category": None,
        "user_budget": "",
        "hour": None,
        "age": None,
        "chosen_grades": None,
        "chosen_index": None,
        "df_models": ImmutableDataFrame(
            pd.DataFrame({"category_name": ["SUV", "Sedan"], "model_id": [1, 2]})
        ),
        "df_parts": ImmutableDataFrame(pd.DataFrame()),
        "df_parts_interior": ImmutableDataFrame(pd.DataFrame()),
        "df_colors": ImmutableDataFrame(pd.DataFrame()),
        "df_grades": ImmutableDataFrame(
            pd.DataFrame(
                {
                    "model_id": [1, 2, 3],
                    "FuelCostPerKilo": [1, 2, 3],
                    "MonthlyMainteCost": [1, 2, 3],
                    "MonthlyInsuranceCost": [1, 2, 3],
                    "price": [1, 2, 3],
                    "MonthlyPriceDropRate": [0.1, 0.1, 0.1],
                }
            )
        ),
        "df_grades_with_cost": None,
    }
    # UserSessionのインスタンスを作成し、デフォルト値を設定
    session = UserSession()
    session.set_default_values(defaults)
    return session


def test_user_input_display_preprocess(user_session):
    display = UserInputDisplay()
    display.preprocess()
    assert "df_models" in st.session_state
    assert "df_parts" in st.session_state
    assert "df_parts_interior" in st.session_state
    assert "df_colors" in st.session_state
    assert "df_grades" in st.session_state


def test_user_input_display_postprocess(user_session):
    display = UserInputDisplay()
    display.car_category = "SUV"
    display.user_budget = "30000"
    display.hour = 10
    display.age = 20
    display.postprocess()
    assert st.session_state["car_category"] == "SUV"
    assert st.session_state["user_budget"] == "30000"
    assert st.session_state["hour"] == 10
    assert st.session_state["age"] == 20


def test_user_input_display_show(user_session):
    display = UserInputDisplay()
    display.preprocess()
    print(st.session_state.df_models)
    display.show()

    # テストはStreamlitのUIコンポーネントの表示を確認するのが難しいため、ここではエラーが出ないかを確認
    assert True


def test_search_result_display_preprocess(user_session):
    display = SearchResultDisplay()
    user_session.set_value("age", 20)
    user_session.set_value("hour", 10)
    display.preprocess()
    assert "df_grades_with_cost" in st.session_state


def test_search_result_display_postprocess(user_session):
    display = SearchResultDisplay()
    display.meets_needs = True
    display.edited_df = pd.DataFrame(
        {
            "check": [True, False],
            "name_desc": ["1.Model1 - Grade1", "2.Model1 - Grade2"],
        }
    )
    display.postprocess()
    assert st.session_state["chosen_grades"] == ["Model1 - Grade1"]


def test_search_result_display_show(user_session):
    display = SearchResultDisplay()
    display.meets_needs = True
    display.df_search_result = pd.DataFrame(
        {
            "image_url": ["img1", "img2"],
            "model_name": ["Model1", "Model2"],
            "name_desc": ["1.Model1 - Grade1", "2.Model1 - Grade2"],
            "MonthlyRealCost": [1000, 2000],
            "MonthlyTotalCost": [1500, 2500],
            "ResaleValue": [500, 1500],
            "rank": [1, 2],
            "check": [False, False],
        }
    )
    display.show()
    # テストはStreamlitのUIコンポーネントの表示を確認するのが難しいため、ここではエラーが出ないかを確認
    assert True


def test_result_comparison_preprocess(user_session):
    # ageとchosen_gradesを設定
    user_session.set_value("age", 5)
    user_session.set_value("hour", 3)
    user_session.set_value("chosen_grades", ["Grade A", "Grade B"])
    user_session.set_value(
        "df_grades",
        ImmutableDataFrame(
            pd.DataFrame(
                {
                    "name_desc": ["Grade A", "Grade B"],
                    "price": [1000000, 1200000],
                    "ResaleValue": [800000, 900000],
                    "MonthlyTotalCost": [30000, 35000],
                    "MainteCost": [20000, 25000],
                    "FuelCostPerKilo": [10, 12],  # FuelCostPerKiloを追加
                    "MonthlyMainteCost": [1000, 1200],  # MonthlyMainteCostを追加
                    "MonthlyInsuranceCost": [500, 600],  # MonthlyInsuranceCostを追加
                    "MonthlyPriceDropRate": [0.01, 0.02],  # MonthlyPriceDropRateを追加
                }
            )
        ),
    )

    display = ResultComparison()
    display.preprocess()
    assert not display.df1.empty
    assert not display.df2.empty
    assert not display.df3.empty


def test_result_comparison_show(user_session):
    # ageとchosen_gradesを設定
    user_session.set_value("age", 5)
    user_session.set_value("hour", 3)
    user_session.set_value("chosen_grades", ["Grade A", "Grade B"])
    user_session.set_value(
        "df_grades",
        ImmutableDataFrame(
            pd.DataFrame(
                {
                    "name_desc": ["Grade A", "Grade B"],
                    "price": [1000000, 1200000],
                    "ResaleValue": [800000, 900000],
                    "MonthlyTotalCost": [30000, 35000],
                    "MainteCost": [20000, 25000],
                    "FuelCostPerKilo": [10, 12],  # FuelCostPerKiloを追加
                    "MonthlyMainteCost": [1000, 1200],  # MonthlyMainteCostを追加
                    "MonthlyInsuranceCost": [500, 600],  # MonthlyInsuranceCostを追加
                    "MonthlyPriceDropRate": [0.01, 0.02],  # MonthlyPriceDropRateを追加
                }
            )
        ),
    )

    display = ResultComparison()
    display.preprocess()
    display.show()
    # テストはStreamlitのUIコンポーネントの表示を確認するのが難しいため、ここではエラーが出ないかを確認
    assert True
