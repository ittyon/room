import streamlit as st
from db.db_queries import get_transaction_years_by_user, get_transactions_by_user, delete_transaction
import pandas as pd
import plotly.express as px

def transactions():
    # 初期描画のみFalseに設定
    if 'balloon_flag_for_delete' not in st.session_state:
        st.session_state.balloon_flag_for_delete = False

    # 削除OKとなった際に、バルーンを表示させて、再度Falseとする
    if st.session_state.balloon_flag_for_delete:
        st.balloons()
        st.session_state.balloon_flag_for_delete = False

    st.header("購入履歴")
    
    years = get_transaction_years_by_user(st.session_state.user_id)
    # print(type(list(years)))  # If it's a NumPy array
    # print(type(years))  # Check the exact type
    # print(list(years))

    # 投資していない場合記載なし
    if years == None:
        return
    
    else:

        select_year = st.selectbox("年を選択してください", list(years[0]), index=0)
        # print(select_year)
        
        data = get_transactions_by_user(st.session_state.user_id)

        # DataFrameに変換
        df = pd.DataFrame(data)
        df.columns = ['stock_code', 'company_name', 'quantity', 'unit_price', 'transaction_date']
        df['transaction_date'] = pd.to_datetime(df['transaction_date'])
        df = df[df['transaction_date'].dt.year == int(select_year)]

        # 月別、銘柄別に購入金額を集計
        df['purchase_amount'] = df['quantity'] * df['unit_price']  # 購入金額を計算
        df['month'] = df['transaction_date'].dt.to_period('M')        # 月別に集計用の列を作成

        # 月別、銘柄別に購入金額を合計
        monthly_data = df.groupby(['month', 'stock_code', 'company_name']).agg({'purchase_amount': 'sum'}).reset_index()
        
        # 数値列に変換
        monthly_data['purchase_amount'] = pd.to_numeric(monthly_data['purchase_amount'], errors='coerce')
        
        
        # 1〜12月の月データを準備
        all_months = pd.DataFrame({
            'japanese_month': [f'{i}月' for i in range(1, 13)]
        })

        monthly_data['japanese_month'] = monthly_data['month'].dt.month.astype(str) + '月'
        monthly_data = all_months.merge(monthly_data, on='japanese_month', how='left').fillna({'purchase_amount': 0})
        # print(all_months)
        # print(monthly_data)
        

        # month列を文字列型に変換
        # monthly_data['month'] = monthly_data['month'].astype(str)

        # Plotlyで棒グラフ（銘柄ごとに色分けされた積み上げグラフ）を作成
        fig = px.bar(
            monthly_data,
            x='japanese_month', 
            y='purchase_amount', 
            color='company_name',  # 銘柄ごとに色分け
            title="月別の購入金額（銘柄ごと）",
            labels={"japanese_month": "購入月", "purchase_amount": "購入金額", "company_name": "銘柄"},
            text='purchase_amount',  # 棒に購入金額を表示
            barmode='stack'  # 積み上げグラフとして表示
        )

        # fig.update_xaxes(tickmode='array', tickvals=all_months,ticktext=all_months)
        # fig.update_xaxes(categoryorder='array', categoryarray=[f'{i}月' for i in range(1, 13)])

        fig.update_xaxes(
            type='category',
            categoryorder='array',
            categoryarray=[f'{i}月' for i in range(1, 13)]
        )

        # Streamlitで表示
        st.plotly_chart(fig)

        # 購入明細
        with st.expander("購入明細"):
            
            df = pd.DataFrame(data)
            df.columns = ['銘柄コード', '銘柄名', '購入株数', '購入単価', '購入日付']
            df['購入日付'] = pd.to_datetime(df['購入日付'])
            df = df[df['購入日付'].dt.year == int(select_year)]
            df['購入日付'] = df['購入日付'].dt.strftime('%Y/%m/%d')

            st.dataframe(
                df,
                hide_index=True,
                use_container_width=True
            )
            
            # df = pd.DataFrame(data)
            # df.columns = ['銘柄コード', '銘柄名', '購入株数', '購入単価', '購入日付']
            # # st.write(df)
            # for index, row in df.iterrows():
            #     col1, col2, col3, col4, col5, col_delete = st.columns([1, 1, 1, 1, 1, 1])
                
            #     # 各列のデータを表示
            #     col1.write(row["銘柄コード"])
            #     col2.write(row["銘柄名"])
            #     col3.write(row["購入株数"])
            #     col4.write(row["購入単価"])
            #     col5.write(row["購入日付"])

            #     # 削除ボタンの表示
            #     if col_delete.button("削除", key=(row["銘柄コード"], row["購入日付"])):
            #         # delete_record(row["id"])  # DBからレコード削除
            #         st.success("削除成功")

        # 削除
        with st.expander("登録削除"):
            st.write("間違えて登録した取引を削除します。")
            
            options = df["銘柄名"].drop_duplicates().tolist()
            options = ["選択してください"] + options
            selected_delete_stock_name = st.selectbox("銘柄を選んでください", options, index=0)

            if selected_delete_stock_name != "選択してください":
                options2 = df[df['銘柄名'] == selected_delete_stock_name]["購入日付"]
                selected_delete_stockdate = st.selectbox("削除する対象の日付を選んでください", options2)

                delete = st.button("削除")
                if delete:

                    # 削除したい取引をDBから削除
                    selected_delete_stock = df[df["銘柄名"] == selected_delete_stock_name]["銘柄コード"].drop_duplicates().tolist()
                    delete_transaction(selected_delete_stock, selected_delete_stockdate.replace("/", "-"), st.session_state.user_id)
                    
                    # バルーンフラグをTrueとし、再描画
                    st.session_state.balloon_flag_for_delete = True
                    st.rerun()

