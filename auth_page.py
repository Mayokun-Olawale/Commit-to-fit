import streamlit as sl
from data_fetcher import get_user_workouts, insert_user_post,get_user_sensor_data
from modules import login_box, signup_box
from datetime import datetime
import pandas as pd
from google.cloud import bigquery

def display_auth():
    sl.subheader("Welcome! Please choose an option.")

    col1, col2 = sl.columns(2)

    if 'auth_mode' not in sl.session_state:
        sl.session_state.auth_mode = 'login'  # default

    with col1:
        if sl.button("🔐 Log In"):
            sl.session_state.auth_mode = 'login'

    with col2:
        if sl.button("📝 Sign Up"):
            sl.session_state.auth_mode = 'signup'

    sl.write("---")  # separator

    if sl.session_state.auth_mode == 'login':
        login_box()
    elif sl.session_state.auth_mode == 'signup':
        signup_box()


def logout():
    sl.session_state.clear()
    sl.query_params.clear()
    sl.rerun()
