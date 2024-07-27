import pandas as pd
import numpy as np
import streamlit as st
from PIL import Image
import requests
import os
from io import BytesIO

def load_data():
    df_models = pd.read_csv("asset/models.csv")
    df_parts = pd.read_csv("asset/exterior_parts.csv")
    df_parts["option_grade_id"] = range(len(df_parts))#ユニークid付与
    df_grades = pd.read_csv("asset/grades.csv")
    # nameだけではユニークにならないので、説明文も追加する
    df_grades["name_desc"] = np.vectorize(lambda name, desc: f"{name} ({desc})")(df_grades["grade_name"], df_grades["desc"])
    return df_models, df_parts, df_grades

def show_selection(df, target_columns, label):
    user_choise = st.selectbox(label=label,options=[""]+df[target_columns].tolist())
    return user_choise

def show_data_as_table(df, caption_column, image_column, colum_count):
    idx = 0
    for _ in range(len(df)-1):
        cols = st.columns(colum_count)
        for i in range(colum_count):
            if idx < len(df):
                cols[i].image(df[image_column].iloc[idx],width=150, caption=df[caption_column].iloc[idx])
                idx += 1
            else:
                break
        if idx >= len(df):
            break

def show_data_as_table_and_select(df, key_prefix, caption_column, image_column, id_column, colum_count):
    container = st.markdown('<div class="scrollable-container">', unsafe_allow_html=True) 
    selected_images = []
    image_urls = df[image_column].tolist()
    names = df[caption_column].tolist()
    ids = df[id_column].tolist()
    for i in range(0, len(df), colum_count):
        cols = st.columns(colum_count)
        for j, col in enumerate(cols):
            if i + j < len(image_urls):
                image_url = image_urls[i + j]
                name = names[i + j]
                name = name if len(name)<10 else name[:10]+"..."
                target_id = ids[i + j]
                if col.checkbox(name, key=key_prefix+str(i+j)):
                    selected_images.append(target_id)
                col.image(image_url, caption="", use_column_width=True)
    return selected_images

if __name__ == "__main__":
    df_models, df_parts, df_grades = load_data()

    target_model = show_selection(df=df_models, label="モデルを選択してください", target_columns="model_name")
    if target_model=="":
        show_data_as_table(df_models, caption_column="model_name", image_column="img_url", colum_count=4)
    else:
        target_model_id = df_models[df_models.model_name==target_model].model_id.iloc[0]

        df_grades_target = df_grades.query("model_id==@target_model_id")
        st.image(df_models[(df_models.model_id==target_model_id)].img_url.iloc[0])
        target_grade = show_selection(df=df_grades_target, label="グレードを選択してください", target_columns="name_desc")
        if target_grade!="":
            target_model_price = df_grades_target.query("name_desc==@target_grade").price.iloc[0]
            target_model_price = int(target_model_price)
            header_placeholder = st.empty()# ヘッダーに初期メッセージを表示
            billing_message = f"現在の金額は{target_model_price}円です。\n - 基本料金：{target_model_price}円"
            header_placeholder.write(billing_message)

            target_grade_id = df_grades_target[df_grades_target.name_desc==target_grade].grade_id.iloc[0]
            df_parts_target = df_parts.query("model_id==@target_model_id and grade_id==@target_grade_id")
            target_parts_ids = show_data_as_table_and_select(df_parts_target, 
                                key_prefix=f"parts_gradeid_{target_grade_id}", 
                                caption_column="name", image_column="img_url", 
                                id_column="option_grade_id", colum_count=4)
            parts_name_list = df_parts.query("option_grade_id in @target_parts_ids").name.tolist()
            price_list = df_parts.query("option_grade_id in @target_parts_ids").price.astype(int).tolist()
            billing_message = f"現在の金額は{target_model_price+sum(price_list)}円です。\n - 基本料金：{target_model_price}円"
            for name, price in zip(parts_name_list, price_list):
                billing_message += f"\n - {name}: {price}"
            header_placeholder.write(billing_message)