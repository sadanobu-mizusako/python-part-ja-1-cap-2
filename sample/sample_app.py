import pandas as pd
import numpy as np
import streamlit as st

df = pd.read_csv("asset/models.csv")
df_parts = pd.read_csv("asset/exterior_parts.csv")
# print(df)

st.title('Multiple Images')
target_model = ""
target_model = st.selectbox(label='モデルを選択してください',
                 options=[""]+df.model_name.tolist())

if target_model=="":
    idx = 0
    for _ in range(len(df)-1):
        cols = st.columns(4)
        for i in range(4):
            if idx < len(df):
                cols[i].image(df.img_url.iloc[idx],width=150, caption=df.model_name.iloc[idx])
                idx += 1
            else:
                break

else:
    idx2 = 0
    target_id = df[df.model_name==target_model].model_id.iloc[0]
    st.image(df[df.model_name==target_model].img_url.iloc[0])
    df_parts_ = df_parts.query("model_id==@target_id")
    for _ in range(len(df_parts_)-1):
        cols = st.columns(4)
        for i in range(4):
            if idx2 < len(df_parts_):
                cols[i].image(df_parts_.img_url.iloc[idx2],width=150, caption=df_parts_.name.iloc[idx2])
                idx2 += 1
            else:
                break
