# import pytest
# import pandas as pd
# from page import UserInputDisplay, SearchResultDisplay

# @pytest.fixture
# def user_input_display():
#     return UserInputDisplay()

# @pytest.fixture
# def search_result_display():
#     return SearchResultDisplay()

# def test_is_number(user_input_display):
#     assert user_input_display._is_number("123") == True
#     assert user_input_display._is_number("abc") == False
#     assert user_input_display._is_number("123.45") == True

# def test_preprocess(user_input_display):
#     # データベースからのデータをモックとして提供
#     df_models = pd.DataFrame({'category_name': ['SUV', 'Sedan']})
#     df_parts = pd.DataFrame({'part_id': [1, 2]})
#     df_parts_interior = pd.DataFrame({'part_interior_id': [1, 2]})
#     df_colors = pd.DataFrame({'color_id': [1, 2]})
#     df_grades = pd.DataFrame({'grade_id': [1, 2]})
    
#     user_input_display.load_data_from_DB = lambda: (df_models, df_parts, df_parts_interior, df_colors, df_grades)
#     user_input_display.preprocess()
    
#     assert user_input_display.state["df_models"].equals(df_models)
#     assert user_input_display.state["df_parts"].equals(df_parts)
#     assert user_input_display.state["df_parts_interior"].equals(df_parts_interior)
#     assert user_input_display.state["df_colors"].equals(df_colors)
#     assert user_input_display.state["df_grades"].equals(df_grades)

# def test_calculate_costs(search_result_display):
#     # テスト用のデータを設定
#     df_grades = pd.DataFrame({
#         'model_id': [1, 2],
#         'FuelCostPerKilo': [0.1, 0.2],
#         'MonthlyMainteCost': [100, 200],
#         'MonthlyInsuranceCost': [50, 100],
#         'price': [10000, 20000],
#         'MonthlyPriceDropRate': [0.01, 0.02]
#     })
    
#     search_result_display.state = {
#         'df_grades': df_grades,
#         'age': 5,
#         'hour': 2
#     }
    
#     search_result_display.calculate_costs(search_result_display.state['age'], search_result_display.state['hour'])
    
#     assert search_result_display.state['df_grades']["FuelCost"].equals(pd.Series([3600, 7200], name="FuelCost"))
#     assert search_result_display.state['df_grades']["MainteCost"].equals(pd.Series([6000, 12000], name="MainteCost"))
#     assert search_result_display.state['df_grades']["ResaleValue"].equals(pd.Series([9044, 18039], name="ResaleValue"))

# def test_search_car_meet_customer_needs(search_result_display):
#     # テスト用のデータを設定
#     df_models = pd.DataFrame({'category_name': ['SUV', 'Sedan'], 'model_id': [1, 2]})
#     df_grades = pd.DataFrame({
#         'model_id': [1, 2],
#         'MonthlyRealCost': [500, 1500],
#         'name_desc': ['Grade A', 'Grade B'],
#         'image_url': ['url1', 'url2'],
#         'rank': [1, 2]
#     })
    
#     search_result_display.state = {
#         'df_models': df_models,
#         'df_grades': df_grades,
#         'car_category': 'SUV',
#         'user_budget': '10000'
#     }
    
#     search_result_display.search_car_meet_customer_needs()
    
#     assert search_result_display.meets_needs == True
#     assert search_result_display.df_search_result.equals(df_grades[df_grades['model_id'] == 1])
