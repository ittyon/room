import requests
import streamlit as st
import json
from config.config import JQUANTS_MAIL, JQUANTS_PASSWORD 

def jquants():
    # 登録したメールアドレス、パスワードを設定
    # EMAIL_ADDRESSに登録メールアドレス、PASSWORDにパスワードを入力
    mail_password={"mailaddress":JQUANTS_MAIL, "password":JQUANTS_PASSWORD}

    # リフレッシュトークン取得
    r_ref = requests.post("https://api.jquants.com/v1/token/auth_user", data=json.dumps(mail_password))

    ######### IDトークン取得 ###########
    # IDトークンの有効期間は２４時間

    # 受け取ったリフレッシュトークンを設定
    RefreshToken = r_ref.json()["refreshToken"]

    # IDトークン取得
    r_token = requests.post(f"https://api.jquants.com/v1/token/auth_refresh?refreshtoken={RefreshToken}")

    # 取得したIDトークンを設定
    idToken = r_token.json()["idToken"]
    st.session_state.jquants_idToken = idToken