import streamlit as st
DB_HOST=st.secrets["DB_HOST"]
DB_PORT=st.secrets["DB_PORT"]
DB_NAME=st.secrets["DB_NAME"]
DB_USER=st.secrets["DB_USER"]
DB_PASSWORD=st.secrets["DB_PASSWORD"]

JQUANTS_MAIL=st.secrets["JQUANTS_MAIL"]
JQUANTS_PASSWORD=st.secrets["JQUANTS_PASSWORD"]

SECRET_KEY=st.secrets["SECRET_KEY"]