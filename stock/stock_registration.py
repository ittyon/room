import streamlit as st
from db.db_queries import insert_stock, get_hold_stock_by_code, get_stock_name
import unicodedata
import requests

def registration():
    # 初期描画のみFalseに設定
    if 'balloon_flag' not in st.session_state:
        st.session_state.balloon_flag = False

    # 売買登録OKとなった際に、バルーンを表示させて、再度Falseとする
    if st.session_state.balloon_flag:
        st.balloons()
        st.session_state.balloon_flag = False

    st.header("株売買登録")
    st.write("ここで売買した株を登録します。")
    
    # 株式登録フォーム
    form = st.form(key='stock_form')
    transaction_date = form.date_input("売買日付を入力してください", value="today")
    transaction_type = form.radio("取引種別", ["購入", "売却"])
    stock_code = form.text_input("銘柄コードを入力してください", placeholder="例: 1234")
    unit_price = form.number_input("売買単価を入力してください", min_value=0, value=1000)
    quantity = form.number_input("売買株数を入力してください", min_value=0, value=100)
    submit_stock_button = form.form_submit_button(label='登録')

    # 銘柄コードを半角変換
    stock_code = unicodedata.normalize('NFKC', stock_code)

    # 銘柄コードから会社名を取得
    stock_name = get_stock_name(stock_code)

    if submit_stock_button:
        if len(stock_code) != 4 or (stock_code.isdigit() == False):
            st.error("銘柄コードは4桁の数字を入力してください")
        elif stock_name is None:
            st.error(f"銘柄コード{stock_code}は存在しません")
        elif transaction_type == "売却" and get_hold_stock_by_code(stock_code, st.session_state.user_id) < quantity:
            st.error(f"銘柄コード({stock_code})は{get_hold_stock_by_code(stock_code, st.session_state.user_id)}株まで売却可能です。")
        else:
            confirm(transaction_date, transaction_type, stock_code, stock_name, unit_price, quantity)

@st.dialog("確認")
def confirm(transaction_date, transaction_type, stock_code, stock_name, unit_price, quantity):

    date = transaction_date.strftime("%Y/%m/%d")
    st.write("以下の内容でよろしいでしょうか？")
    st.write(f"売買日付：{date}")
    st.write(f"取引種別：{transaction_type}")
    st.write(f"企業名：{stock_name}")
    st.write(f"売買単価：{unit_price}")
    st.write(f"売買株数：{quantity}")

    # 取引種別変換
    transaction_type = "buy" if transaction_type == "購入" else "sell"

    if st.button("OK"):

        # 購入株をDBに登録
        insert_stock(stock_code, transaction_type, quantity, unit_price, date, st.session_state.user_id)

        # バルーンフラグをTrueとし、再描画
        st.session_state.balloon_flag = True
        st.rerun()
        