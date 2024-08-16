import pytest
import pandas as pd
from base_page import BaseDisplay, UtilityElement

# テスト用の BaseDisplay のモック実装
class MockDisplay(BaseDisplay):
    def preprocess(self):
        """preprocess が呼び出されたことを示すフラグを設定"""
        self.preprocessed = True

    def show(self):
        """show が呼び出されたことを示すフラグを設定"""
        self.shown = True

    def postprocess(self):
        """postprocess が呼び出されたことを示すフラグを設定"""
        self.postprocessed = True

# # TestDisplay クラスのインスタンスを作成するフィクスチャ
# フィクスチャにはスコープを設定することができます。スコープには以下の種類があります：
# - `function`（デフォルト）：各テスト関数の実行前にフィクスチャを実行し、後にテアダウン（テストが終了した後に行うクリーンアップ作業）を行います。
# - `class`：クラス内のすべてのテストメソッドの実行前にフィクスチャを実行し、後にテアダウンを行います。
# - `module`：モジュール内のすべてのテスト関数の実行前にフィクスチャを実行し、後にテアダウンを行います。
# - `package`：パッケージ内のすべてのテスト関数の実行前にフィクスチャを実行し、後にテアダウンを行います。
# - `session`：テストセッション全体の実行前にフィクスチャを実行し、後にテアダウンを行います。
@pytest.fixture(scope="function")
def mock_display():
    """MockDisplay のインスタンスを返すフィクスチャ"""
    return MockDisplay()

# BaseDisplay 抽象クラスのメソッドが正しく呼び出されることを確認するテスト
def test_base_display(mock_display):
    """
    MockDisplay インスタンスが正しく初期化され、
    各メソッドが呼び出されたことを確認するテスト
    """
    mock_display.run()
    assert mock_display.preprocessed  # preprocess が呼び出されたことを確認
    assert mock_display.shown         # show が呼び出されたことを確認
    assert mock_display.postprocessed # postprocess が呼び出されたことを確認

# UtilityElement クラスのインスタンスを作成するフィクスチャ
@pytest.fixture(scope="function")
def utility_element():
    """UtilityElement のインスタンスを返すフィクスチャ"""
    return UtilityElement()

# UtilityElement の _show_data_as_table_and_select メソッドをテスト
def test_show_data_as_table_and_select(utility_element, mocker):
    """
    UtilityElement の _show_data_as_table_and_select メソッドが正しく動作するかをテスト
    """
    # テストデータを DataFrame として準備
    data = {
        'caption': ['Image 1', 'Image 2', 'Image 3'],
        'image_url': ['url1', 'url2', 'url3'],
        'id': [1, 2, 3]
    }
    df = pd.DataFrame(data)

    # Streamlit の columns 関数をモックしてモックカラムを返す
    mock_columns = [mocker.Mock() for _ in range(3)] #streamlit.columnsが呼び出されたときに返される値
    mocker.patch('streamlit.columns', return_value=mock_columns) #テスト用にstreamlit.columnsをモックオブジェクトに置き換え。
    
    # モックされた checkbox 関数の副作用を定義
    def checkbox_side_effect(name, key):
        """
        特定のキーに対して True を返し、ユーザー選択をシミュレーション
        """
        return key in ['test_0', 'test_2']

    # 各モックカラムに対して checkbox と image メソッドをモック
    for mock_col in mock_columns:
        mock_col.checkbox = mocker.Mock(side_effect=checkbox_side_effect)# side_effectでmocker.Mockが呼び出された時の挙動を定義
        mock_col.image = mocker.Mock()

    # テスト対象メソッドを呼び出し、選択された画像を取得
    selected_images = utility_element._show_data_as_table_and_select(df, 'test_', 'caption', 'image_url', 'id', 3)
    
    # 選択された画像が期待通りであることを確認
    assert selected_images == [1, 3]
