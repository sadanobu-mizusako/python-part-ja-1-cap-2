import streamlit as st

# セッションステートの初期化
# if 'selectbox' not in st.session_state:
#     st.session_state.selectbox = ""

# コールバック関数を定義してセレクトボックスの値をリセット
def reset_selectbox():
    st.session_state.selectbox = ""

# 要件1: デフォルトの選択肢は空文字
options = ["", "選択肢1", "選択肢2", "選択肢3"]
selected_option = st.selectbox("選択してください", options, key="selectbox")

# 要件2: 空文字以外が選択されるまでページ下部は表示されない
if selected_option != "":
    with st.form(key="personal_info_form"):
        st.write("個人情報を入力してください")

        name = st.text_input("名前")
        email = st.text_input("メールアドレス")
        submit_button = st.form_submit_button(label="送信", on_click=reset_selectbox)

        if submit_button:
            st.write(f"ありがとうございます、{name}さん！")
            # フォーム送信時にセレクトボックスをリセットする
            st.experimental_rerun()
else:
    st.write("オプションを選択してください。")
