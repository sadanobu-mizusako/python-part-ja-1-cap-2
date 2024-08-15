from abc import ABC, abstractmethod
import streamlit as st

class BaseDisplay(ABC):
    """
    ページの挙動を定める要素。前処理、可視化、後処理の3つで構成する
    """
    def __init__(self) -> None:
        self.preprocess()
        self.show()
        self.postprocess()

    @abstractmethod
    def preprocess():
        pass

    @abstractmethod
    def show():
        pass

    @abstractmethod
    def postprocess():
        pass

class UtilityElement:
    """
    汎用的に使えるエレメントを定義
    """
    def _show_data_as_table_and_select(self, df, key_prefix, caption_column, image_column, id_column, colum_count):
        """
        複数の画像と「チェックボックス」を並べて表示してユーザーに選択させるためのビジュアル要素
        - df: オプション選択肢を含んだデータフレーム
        - key_prefix: keyの前に共通でつけるプレフィックス。各オブジェクトのkeyはkey_prefix_[要素の番号]の形式でsession_stateに保存される
        - caption_column: 画像のキャプションを指定する列名
        - image_column: 画像のURLを指定する列名
        - id_column: 対象を識別するidを指定する列名　#ここでは使用していない。。
        - colum_count: 横何列に並べるかを指定する
        """
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