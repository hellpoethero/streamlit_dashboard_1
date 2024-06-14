import streamlit as st
import numpy as np
import pandas as pd
import datetime
import plotly.graph_objects as go
from st_pages import show_pages_from_config, add_page_title
import random
from utils import DataLoader

add_page_title(layout="wide")
show_pages_from_config()
state = st.session_state

df = DataLoader.load_sootblow()
max_time = df["start_datetime"].max()
min_time = df["start_datetime"].max() - pd.to_timedelta(1, unit="d")

row = st.columns(4)
d = row[0].date_input(
    "Chọn thời gian bắt đầu",
    (max_time, max_time),
    df["start_datetime"].min(),
    df["start_datetime"].max(),
    format="MM/DD/YYYY",
    key="d",
)

option1 = row[1].selectbox(
    "Chọn nhóm vòi thổi", ["Tất cả", "Nhóm 2", "Nhóm 3"] 
)

if len(st.session_state.d)==2:
    group = [[2,3], [2], [3]][["Tất cả", "Nhóm 2", "Nhóm 3"].index(option1)]
    print(pd.to_datetime(st.session_state.d[0]), pd.to_datetime(st.session_state.d[1]))
    print(group)
    # show_df = df[(df['start_datetime']>=pd.to_datetime(st.session_state.d[0])) & (df['start_datetime']<=pd.to_datetime(st.session_state.d[1])) & (df['group'].isin(group))]
    cols = ["group","cycle_full_gr","start_datetime","finish_datetime",'duration (minutes)']
    show_df = df[(df['start_datetime'].dt.date>=st.session_state.d[0]) & (df['start_datetime'].dt.date<=st.session_state.d[1]) & (df['group'].isin(group))][cols]
    # show_df = df[df['group'].isin(group)]
    st.dataframe(show_df, use_container_width=True)

