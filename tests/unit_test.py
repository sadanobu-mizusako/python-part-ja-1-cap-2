# ファイル: ./tests/unit_test.py

import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
import numpy as np
import streamlit as st
import sys
sys.path.append('..')
from main_app import CustomizationPage

class TestCustomizationPage(unittest.TestCase):

    @patch('main_app.SQliteManager')
    def setUp(self, MockSQliteManager):
        """
        テスト用のデータ用意
        """
        self.page = CustomizationPage()

        # テスト用のデータを設定
        df_models = pd.DataFrame({
            'model_id': [1, 2],
            'category_name': ['SUV', 'Sedan'],
            'model_name': ['Model X', 'Model Y'],
            'img_url': ['http://example.com/model_x.jpg', 'http://example.com/model_y.jpg']
        })

        df_grades = pd.DataFrame({
            'model_id': [1, 1, 2, 2],
            'grade_id': [1, 2, 3, 4],
            'grade_name': ['Grade A', 'Grade B', 'Grade C', 'Grade D'],
            'price': [30000, 40000, 50000, 60000],
            'desc': ['Description A', 'Description B', 'Description C', 'Description D'],
            'FuelCostPerKilo': [10, 12, 14, 16],
            'MonthlyMainteCost': [100, 120, 140, 160],
            'MonthlyInsuranceCost': [100, 120, 140, 160],
            'MonthlyPriceDropRate': [0.01, 0.02, 0.03, 0.04],
            'name_desc': ['Grade A (Description A)', 'Grade B (Description B)', 'Grade C (Description C)', 'Grade D (Description D)'],
            'MonthlyRealCost': [2000, 3000, 4000, 5000]
        })

        df_parts = pd.DataFrame({
            'option_grade_id': [1, 2, 3, 4],
            'grade_id': [1, 2, 3, 4],
            'model_id': [1, 1, 2, 2],
            'name': ['Part A', 'Part B', 'Part C', 'Part D'],
            'price': [1000, 2000, 3000, 4000],
            'img_url': ['http://example.com/part_a.jpg', 'http://example.com/part_b.jpg', 'http://example.com/part_c.jpg', 'http://example.com/part_d.jpg']
        })

        self.page.df_models = df_models
        self.page.df_grades = df_grades
        self.page.df_parts = df_parts

    def test_show_selection(self):
        """
        リストから1つのオプションを選択するためのビジュアル要素のテスト。
        """
        with patch('streamlit.selectbox') as mock_selectbox:
            mock_selectbox.return_value = "Model X"
            selected_model = self.page._show_selection(self.page.df_models, 'model_name', 'モデルを選択してください', 'select_model')
            self.assertEqual(selected_model, "Model X")

    def test_show_data_as_table(self):
        """
        複数の画像を並べて表示するためのビジュアル要素のテスト。
        """
        with patch('streamlit.columns') as mock_columns:
            mock_col = MagicMock()
            mock_columns.return_value = [mock_col, mock_col, mock_col, mock_col]
            self.page._show_data_as_table(self.page.df_models, 'model_name', 'img_url', 4)
            self.assertTrue(mock_col.image.called)

    def test_user_request(self):
        """
        ユーザーの要望入力フォームのテスト。
        """
        with patch('streamlit.selectbox') as mock_selectbox, patch('streamlit.text_input') as mock_text_input:
            mock_selectbox.return_value = 'SUV'
            mock_text_input.return_value = '700000'
            self.assertTrue(self.page.user_request())

    def test_how_user_drives(self):
        """
        ユーザーの乗り方入力フォームのテスト。
        """
        with patch('streamlit.selectbox') as mock_selectbox:
            mock_selectbox.side_effect = [5, 2]
            self.assertTrue(self.page.how_user_drives())

    def test_search_car_meet_customer_needs(self):
        """
        ユーザーの要望に合う車両を検索する関数のテスト。
        """
        self.page.category = 'SUV'
        self.page.year_cost = '700000'
        self.page.hold_month = 60
        self.page.hour_per_day = 2
        self.assertTrue(self.page._search_car_meet_customer_needs())
        self.assertGreater(len(st.session_state.search_result), 0)

    def test_model_seletion(self):
        """
        モデル選択ページのテスト。
        """
        with patch('streamlit.selectbox') as mock_selectbox:
            mock_selectbox.return_value = 'Model X'
            self.assertTrue(self.page.model_seletion())

    def test_grade_seletion(self):
        """
        グレード選択ページのテスト。
        """
        self.page.target_model = 'Model X'
        with patch('streamlit.selectbox') as mock_selectbox, patch('streamlit.image'):
            mock_selectbox.return_value = 'Grade A (Description A)'
            self.assertTrue(self.page.grade_seletion())

    def test_show_total_price(self):
        """
        合計金額表示ページのテスト。
        """
        self.page.target_model = 'Model X'
        self.page.target_grade = 'Grade A (Description A)'
        self.page.df_grades_target = self.page.df_grades[self.page.df_grades['model_id'] == 1]  # テスト用にdf_grades_targetを設定
        self.page.show_total_price()
        self.assertEqual(self.page.total_price, 30000)

    def test_parts_selection(self):
        """
        オプション選択ページのテスト。
        """
        self.page.target_model_id = 1
        self.page.target_grade_id = 1
        with patch('streamlit.columns') as mock_columns, patch('streamlit.checkbox') as mock_checkbox, patch('streamlit.image'):
            mock_col = MagicMock()
            mock_columns.return_value = [mock_col, mock_col, mock_col, mock_col]
            mock_checkbox.return_value = True
            self.assertTrue(self.page.parts_selection())

if __name__ == '__main__':
    unittest.main()