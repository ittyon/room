import streamlit as st
from streamlit_option_menu import option_menu
from config import jquants_connection
from stock import stock_registration, stock_transactions, stock_dividend
import streamlit_authenticator as stauth
from db.db_queries import get_users
from config.config import SECRET_KEY

# ログイン

# DBからユーザ情報取得
users = get_users()
# st.write(users)

# Streamlit Authenticator 用の辞書形式に変換
credentials = {"usernames": {}}
for username, name, hashed_password, email, id in users:
    credentials["usernames"][username] = {
        "name": name,
        "password": hashed_password,  # ハッシュ化されたパスワード
        "email": email,
        # 必要に応じて roles を追加
        # "roles": ["users"]
    }

# credentials = {"usernames": {
#     "itsuki": {
#         "name": "いっちょん",
#         "password": "$2b$12$xhid67NmhJ2cP7zKwSvTsOlzMC/DSVGrSZ/sGx8KLCrAfyT5aGUYq",
#         "email": "negroponte8528@gmail.com",
#     }
# }}
# authenticator = stauth.Authenticate(
#     credentials, cookie_name="auth", key="abcd", cookie_expiry_days=30
# )

# st.write(credentials)


# 認証設定
authenticator = stauth.Authenticate(
    credentials,
    "room_app",
    SECRET_KEY,
    cookie_expiry_days=30
)

# ユーザー認証
# authentication_status = authenticator.login("main")
# authentication_status = authenticator.login("sidebar")
# name, authentication_status = authenticator.login("ログインフォーム", "main")
# name, authentication_status = authenticator.login(location="main", form_name="ログインフォーム")
# name, authentication_status = authenticator.login("main")


# st.write(st.session_state.name)
# st.write(st.session_state.username)
# st.write(st.session_state.email)
# st.write(st.session_state)
# st.write(authentication_status)
# st.write(st.session_state.authentication_status)

# 認証結果の処理
# if authentication_status is None:
#     st.warning("ユーザー名とパスワードを入力してください。")
# elif authentication_status:
#     st.success(f"ログイン成功: {name}さん、ようこそ！")
# else:
#     st.error("ユーザー名またはパスワードが正しくありません。")



if st.session_state.authentication_status == False:
    authenticator.login("main")
    st.error("ユーザ名かパスワードが間違っています。")

if st.session_state.authentication_status == None:
    authenticator.login("main")
    st.warning("ユーザ名とパスワードを入力してください。")

if st.session_state.authentication_status == True:

    # ユーザIDをセッションに登録
    # if 'user_id' not in st.session_state:
    user_id = None
    for row in users:
        if row[0] == st.session_state.username:
            user_id = row[4]
    st.session_state.user_id = user_id
    # st.write(st.session_state.user_id)

    st.sidebar.write(f"{st.session_state.name}")

    main_function = st.sidebar.selectbox("部屋を選択してください", ["ホーム", "株"], 0)

    if main_function == "ホーム":
        # st.rerun()
        st.title("Welcome")

    elif main_function == "株":
        # 初回のみjquantsのidTokenを取得
        if 'jquants_idToken' not in st.session_state:
            jquants_connection.jquants()

        # 株のサイドバー
        with st.sidebar:
            selected = option_menu(
                menu_title = "メニュー",
                options = ["配当金", "株売買登録", "購入履歴"],
                icons = ["bi bi-piggy-bank", "bi bi-cart3", "bi bi-clock-history"],
                menu_icon = "bi bi-list",
                default_index = 0
            )

        if selected == "配当金":
            # st.title("配当金")
            stock_dividend.dividend()

        elif selected == "株売買登録":
            stock_registration.registration()

        elif selected == "購入履歴":
            stock_transactions.transactions()
        

    elif main_function == "やりたいこと":

        # やりたいことのサイドバー
        with st.sidebar:
            selected = option_menu(
                menu_title = "Menu",
                options = ["やりたいこと登録", "やりたいことリスト"],
                icons = ["house-heart-fill", "calendar2-heart-fill", "envelope-heart-fill"],
                menu_icon = "emoji-heart-eyes-fill",
                default_index = 0
            )

    with st.sidebar:

        # ログアウト表示
        authenticator.logout("ログアウト")