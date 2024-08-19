import pytest
import streamlit as st
from session_manager.base_user_session import BaseUserSession

# pytestのフィクスチャを使って、新しいユーザーセッションのインスタンスを作成
@pytest.fixture
def user_session():
    # Streamlitのセッションステートをクリアして初期状態にする
    st.session_state.clear()
    # BaseUserSessionのインスタンスを返す
    return BaseUserSession()

# set_default_valuesメソッドのテスト
def test_set_default_values(user_session):
    # デフォルト値を設定
    defaults = {'key1': 'value1', 'key2': 2}
    # メソッドを呼び出してデフォルト値を設定
    user_session.set_default_values(defaults)

    # セッションステートにデフォルト値が正しく設定されているか確認
    assert st.session_state['key1'] == 'value1'
    assert st.session_state['key2'] == 2

# set_valueメソッドのテスト
def test_set_value(user_session):
    # セッションステートに初期値を設定
    st.session_state['key1'] = 'initial'
    # メソッドを呼び出して値を更新
    user_session.set_value('key1', 'updated')

    # 値が正しく更新されているか確認
    assert st.session_state['key1'] == 'updated'

    # 存在しないキーを設定しようとするとKeyErrorが発生することを確認
    with pytest.raises(KeyError):
        user_session.set_value('key_invalid', 'value')

# set_valuesメソッドのテスト
def test_set_values(user_session):
    # セッションステートに初期値を設定
    st.session_state['key1'] = 'initial'
    st.session_state['key2'] = 2

    # 更新する値を設定
    values = {'key1': 'updated', 'key2': 5}
    # メソッドを呼び出して値を更新
    user_session.set_values(values)

    # 値が正しく更新されているか確認
    assert st.session_state['key1'] == 'updated'
    assert st.session_state['key2'] == 5

# get_valueメソッドのテスト
def test_get_value(user_session):
    # セッションステートに値を設定
    st.session_state['key1'] = 'value1'

    # 値が正しく取得できるか確認
    assert user_session.get_value('key1') == 'value1'

    # 存在しないキーを取得しようとするとKeyErrorが発生することを確認
    with pytest.raises(KeyError):
        user_session.get_value('key_invalid')
