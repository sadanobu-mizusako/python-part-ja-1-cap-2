import streamlit as st
import pandas as pd
import plotly.express as px

def data_prep():
    data1 = {
        '経過年数': [1, 2, 3, 4, 5 , 1, 2, 3, 4, 5],
        'グレード': ['A', 'A', 'A', 'A', 'A', 'B', 'B', 'B', 'B', 'B'],
        '累計出費': [100, 200, 300, 150, 250, 140, 220, 310, 150, 350]
    }

    data2 = {
        '経過年数': [1, 2, 3, 4, 5 , 1, 2, 3, 4, 5],
        'グレード': ['A', 'A', 'A', 'A', 'A', 'B', 'B', 'B', 'B', 'B'],
        '単年出費': [100, 200, 300, 150, 250, 140, 220, 310, 150, 350]
    }

    data3 = {
        'グレード': ['A', 'B', 'A', 'B', 'A', 'B'],
        '費用項目': ['初期費用', '初期費用', 'メンテコスト', 'メンテコスト', '売却益', '売却益'],
        '累計出費': [150, 150, 100, 150, -100, -120]
    }

    df1 = pd.DataFrame(data1)
    df2 = pd.DataFrame(data2)
    df3 = pd.DataFrame(data3)
    return df1, df2, df3

def compare(df1, df2, df3):
    st.title('ライフサイクルコストの比較')

    col1, col2 = st.columns(2)

    with col1:
        fig1 = px.line(df1, x='経過年数', y='累計出費', color='グレード', title='累計出費 vs 経過年数')
        st.plotly_chart(fig1)

        fig3 = px.bar(df3, x='グレード', y='累計出費', color='費用項目', title='累計出費 vs 費用項目')
        st.plotly_chart(fig3)

    with col2:
        fig2 = px.bar(df2, x='経過年数', y='単年出費', color='グレード', title='単年出費 vs 経過年数', barmode='group')
        st.plotly_chart(fig2)

if __name__=="__main__":
    df1, df2, df3 = data_prep()
    compare(df1, df2, df3)