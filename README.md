# 修了プロジェクトのためのリポジトリ
- サンプルのコードとパーツデータを共有します。

# 環境のセッティング
1. 仮想環境の準備

2~3行目は仮想環境を作成するためのコマンド。一度環境を設定したら、実行する必要はありません。venv以下はgitでシェアされないように.gitigoreに設定済み。
```
cd [プロジェクトフォルダ]
python3 -m venv venv
source venv/Scripts\activate
```

2. 仮想環境へのパッケージのインストール

requirements.txtにstreamlit, numpy, pandas, selenium, pytest, dashをインストールした環境を準備してあります。以下のコマンドで一括インストール可能です。
```
pip install -r requirements.txt
```

3. 自分で新しいパッケージをインストールした場合

以下のコマンドでご自身の環境の情報をrequirements.txtに反映することが可能です。
```
pip freeze > requirements.txt
```

4. サンプルアプリの実行

以下のコマンドを実行ください。
```
streamlit run your_script.py
```

5. その他ファイル

- asset
    - 画像URLやパーツ名などを保存したcsv
- data_collector
    - 上記を収集するためのスクレイピングファイル


