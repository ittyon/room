import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from db.db_queries import get_hold_stock_by_user, get_users
from decimal import Decimal
# import pandas as pd
# from db.db_queries import get_stock

def detail_stock(name, stocks, sum_buy_money, sum_dividend, dividend_per_stock):
    with st.expander(name):

        st.write("") 

        # 投資していない場合はスルー
        if sum_buy_money == 0:
            return
        else:
            # 年間配当金額と利回り表示
            dividend_yield = sum_dividend/sum_buy_money*100 if sum_buy_money != 0 else 0
            st.markdown(f"""
                        <div style='display: flex; justify-content: center; align-items: center;'>
                            <h4 style='text-align: center; font-size: 30px;'>年間配当金額  {int(sum_dividend):,}円</h4>
                            <p style='text-align: center; font-size: 15px; color: gray;margin-top: 25px;'>（配当利回り: {dividend_yield:.2f}%）</p>
                        </div>
                        """, unsafe_allow_html=True)

            st.write("")
            st.text(f"累計投資合計金額  {int(sum_buy_money):,}円")
            
            st.divider()

            st.write("保有銘柄") 

            df = pd.DataFrame(stocks)
            df.columns = ['銘柄コード', '銘柄名', '平均取得単価', '保有株数', 'セクター']
            df = df.reindex(columns=['銘柄コード', '銘柄名', 'セクター', '平均取得単価', '保有株数'])

            # 結合
            df = df.merge(dividend_per_stock, on = "銘柄コード", how = "inner")

            # 配当利回り列追加　sum_dividend/sum_buy_money*100:.2f
            df["配当利回り[%]"] = (df["配当金/株"] / df["平均取得単価"] * 100).astype(float).round(2)

            # 配当合計列追加
            df["配当合計"] = df["保有株数"] * df["配当金/株"]

            # df_2 = df.reindex(columns=['銘柄コード', '銘柄名', '平均取得単価', '保有株数', "配当利回り[%]", "配当合計"])
            df_2 = df.reindex(columns=['銘柄コード', '銘柄名', '平均取得単価', '保有株数', "配当金/株", "配当利回り[%]", "配当合計"])

            # 明細表示
            st.dataframe(
                df_2,
                hide_index=True,
                use_container_width=True
            )

            st.divider()

            st.write("配当ポートフォリオ")
            tab = st.radio("グラフタイプを選択", ("銘柄別", "セクター別"), key=f"{name}")

            if tab == "銘柄別":
                
                # Plotly で円グラフを作成
                # df = df.groupby("セクター")["配当合計"].sum().reset_index()
                df = df.sort_values("配当合計", ascending=False)
                fig = px.pie(df, names='銘柄名', values='配当合計', category_orders={"銘柄名": df["銘柄名"].tolist()})

            elif tab == "セクター別":

                # Plotly で円グラフを作成
                df = df.groupby("セクター")["配当合計"].sum().reset_index()
                df = df.sort_values("配当合計", ascending=False)
                fig = px.pie(df, names='セクター', values='配当合計', category_orders={"セクター": df["セクター"].tolist()})

            # 円グラフ表示
            st.plotly_chart(fig, key=f"{name}_2")

def caluculate_stocks(stocks, sum_buy_money, sum_dividend, df_temp):

    headers = {'Authorization': 'Bearer {}'.format(st.session_state.jquants_idToken)}

    for stock in stocks:
        
        # 保有株の銘柄コード
        code = stock[0]

        # 平均取得金額　＊　保有株数
        sum_buy_money += stock[2] * stock[3]

        # 配当金取得API
        req = requests.get(f"https://api.jquants.com/v1/fins/statements?code={code}", headers=headers)
        datas = req.json()["statements"]

        dividend_all_q = 0 if datas[-1]["ForecastDividendPerShareAnnual"] == "" else Decimal(datas[-1]["ForecastDividendPerShareAnnual"])
        # dividend_1_q = 0 if datas[-1]["ForecastDividendPerShare1stQuarter"] == "" else Decimal(datas[-1]["ForecastDividendPerShare1stQuarter"])
        # dividend_2_q = 0 if datas[-1]["ForecastDividendPerShare2ndQuarter"] == "" else Decimal(datas[-1]["ForecastDividendPerShare2ndQuarter"])
        dividend_3_q = 0 if datas[-1]["ForecastDividendPerShare3rdQuarter"] == "" else Decimal(datas[-1]["ForecastDividendPerShare3rdQuarter"])
        dividend_4_q = 0 if datas[-1]["ForecastDividendPerShareFiscalYearEnd"] == "" else Decimal(datas[-1]["ForecastDividendPerShareFiscalYearEnd"])

        # 年間予想配当データあれば、そのデータ
        if dividend_all_q != 0:
            dividend = dividend_all_q
        # 年間配当がなければ、3q or 4q の*2とする
        else:
            dividend = dividend_3_q * 2 + dividend_4_q * 2
        
        # 保有株の1株当たりの配当金　＊　保有株
        sum_dividend += dividend * stock[3]

        # データを準備
        data = [code, dividend]
        df_temp = pd.concat([df_temp, pd.DataFrame([data], columns=df_temp.columns)], ignore_index = True)

    return sum_buy_money, sum_dividend, df_temp

def dividend():

    st.header("配当金")
    st.write("")

    # 保有株を取得
    stocks_1 = get_hold_stock_by_user(1)
    stocks_2 = get_hold_stock_by_user(2)

    # ユーザごとの合計配当金と合計投資金額を定義
    sum_dividend_1 = 0
    sum_buy_money_1 = 0

    sum_dividend_2 = 0
    sum_buy_money_2 = 0

    sum_dividend = 0
    sum_buy_money = 0

    # ユーザごとの明細コードの配当金データ準備
    # 明細用にコードと1株あたりの配当金のデータを準備
    df_temp_1 = pd.DataFrame(columns=['銘柄コード', '配当金/株'])
    df_temp_2 = pd.DataFrame(columns=['銘柄コード', '配当金/株'])

    # ユーザごとに計算
    sum_buy_money_1, sum_dividend_1, df_temp_1 = caluculate_stocks(stocks_1, sum_buy_money_1, sum_dividend_1, df_temp_1)
    sum_buy_money_2, sum_dividend_2, df_temp_2 = caluculate_stocks(stocks_2, sum_buy_money_2, sum_dividend_2, df_temp_2)

    # 配当金の合計を計算
    sum_dividend = sum_dividend_1 + sum_dividend_2
    sum_buy_money = sum_buy_money_1 + sum_buy_money_2

    # 年間配当金額と利回り表示
    dividend_yield = sum_dividend/sum_buy_money*100 if sum_buy_money != 0 else 0
    st.markdown(f"""
                <div style='display: flex; justify-content: center; align-items: center;'>
                    <h4 style='text-align: center; font-size: 36px;'>2人の年間配当金額  {int(sum_dividend):,}円</h4>
                    <p style='text-align: center; font-size: 20px; color: gray;margin-top: 25px;'>（配当利回り: {dividend_yield:.2f}%）</p>
                </div>
                """, unsafe_allow_html=True)

    st.write("")
    st.text(f"2人の累計投資合計金額  {int(sum_buy_money):,}円")
    st.write("")

    # 明細
    users = get_users()
    detail_stock(f"{users[0][1]}の明細", stocks_1, sum_buy_money_1, sum_dividend_1, df_temp_1)
    detail_stock(f"{users[1][1]}の明細", stocks_2, sum_buy_money_2, sum_dividend_2, df_temp_2)

    # with st.expander("明細"):

    #     st.write("") 

    #     # 投資していない場合はスルー
    #     if sum_buy_money == 0:
    #         return
    #     else:
    #         # st.text(f"累計投資金額  {int(sum_buy_money):,}円")
    #         st.write("") 
    #         st.write("保有銘柄") 

    #         df = pd.DataFrame(stocks)
    #         df.columns = ['銘柄コード', '銘柄名', '平均取得単価', '保有株数', 'セクター']
    #         df = df.reindex(columns=['銘柄コード', '銘柄名', 'セクター', '平均取得単価', '保有株数'])

    #         # 結合
    #         df = df.merge(df_temp, on = "銘柄コード", how = "inner")

    #         # 配当利回り列追加　sum_dividend/sum_buy_money*100:.2f
    #         df["配当利回り[%]"] = (df["配当金/株"] / df["平均取得単価"] * 100).astype(float).round(2)

    #         # 配当合計列追加
    #         df["配当合計"] = df["保有株数"] * df["配当金/株"]

    #         # df_2 = df.reindex(columns=['銘柄コード', '銘柄名', '平均取得単価', '保有株数', "配当利回り[%]", "配当合計"])
    #         df_2 = df.reindex(columns=['銘柄コード', '銘柄名', '平均取得単価', '保有株数', "配当金/株", "配当利回り[%]", "配当合計"])

    #         # 明細表示
    #         st.dataframe(
    #             df_2,
    #             hide_index=True,
    #             use_container_width=True
    #         )

    #         st.divider()

    #         st.write("配当ポートフォリオ")
    #         tab = st.radio("グラフタイプを選択", ("銘柄別", "セクター別"))

    #         if tab == "銘柄別":
                
    #             # Plotly で円グラフを作成
    #             # df = df.groupby("セクター")["配当合計"].sum().reset_index()
    #             df = df.sort_values("配当合計", ascending=False)
    #             fig = px.pie(df, names='銘柄名', values='配当合計', category_orders={"銘柄名": df["銘柄名"].tolist()})

    #         elif tab == "セクター別":

    #             # Plotly で円グラフを作成
    #             df = df.groupby("セクター")["配当合計"].sum().reset_index()
    #             df = df.sort_values("配当合計", ascending=False)
    #             fig = px.pie(df, names='セクター', values='配当合計', category_orders={"セクター": df["セクター"].tolist()})

    #         # 円グラフ表示
    #         st.plotly_chart(fig)

    # # 配当金推移
    # with st.expander("配当金推移"):
        
    #     transactions = get_transactions_by_user(st.session_state.user_id)
    #     df_tran = pd.DataFrame(transactions)
    #     df_tran.columns = ['銘柄コード', '銘柄名', '売買株数', '単価', '日付']
    #     st.write(df_tran)

    # st.write(stocks)

    # req = requests.get("https://api.jquants.com/v1/fins/statements?code=9434", headers=headers)
    # datas = req.json()["statements"]
    # st.write(datas[-1])

    # st.write(type(stocks))

    # st.write(st.session_state.jquants_idToken)

    # # DBからデータを取得
    # results = get_stock()

    # # # 結果をDataFrameに変換
    # df = pd.DataFrame(results)

    # # # テーブルを表示
    # st.dataframe(df)
    # st.dataframe(df)

