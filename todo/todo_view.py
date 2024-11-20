# import streamlit as st
# import pandas as pd
# from db.db_queries import fetch_todo_list

# def view():
#     st.title("やりたいことリスト")
    
#     # DBからデータを取得
#     results = fetch_todo_list()
    
#     # 結果をDataFrameに変換
#     df = pd.DataFrame(results, columns=["記録ユーザ名", "記録日", "やりたいこと", "誰からのおすすめ", "参考URL"])
    
#     # テーブルを表示
#     st.dataframe(df)
