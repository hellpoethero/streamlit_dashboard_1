import streamlit as st
import numpy as np
import pandas as pd
import datetime
from st_pages import show_pages_from_config, add_page_title
import plotly.graph_objects as go
import plotly.express as px
import random
from time import sleep
from utils import DataLoader

add_page_title(layout="wide")
show_pages_from_config()
state = st.session_state

df, df_pred = DataLoader.load_prediction()

if 'show_time' in st.session_state:
    show_time = pd.to_datetime(st.session_state.show_time)
else:
    show_time = df['DateTime'].max()
    st.session_state.show_time = str(show_time)

def changeDatetime():
    show_time = pd.to_datetime(str(st.session_state.d) + " " + str(st.session_state.t))
    st.session_state.show_time = str(show_time)
    print(d,":", t,show_time,st.session_state.show_time)

row1 = st.columns(3)
d = row1[0].date_input(
    "Chọn ngày hiển thị",
    show_time,
    df['DateTime'].min(),
    df['DateTime'].max(),
    format="MM/DD/YYYY",
    key="d",
    on_change=changeDatetime
)
t = row1[1].time_input(
    "Chọn giờ hiển thị",
    show_time,
    key="t",
    on_change=changeDatetime
)

option = row1[2].selectbox("Lựa chọn chỉ số", ["hr","MST_act","HRHT_act","AHAGOT_act","AHBGOT_act"])

# row2 = st.columns([10,2])
# row2_1 = row2[1].columns([1,1])
# if row2_1[0].button("Trước"):
#     print(show_time)
#     show_time = show_time - pd.to_timedelta(15, unit='m')
#     st.session_state.show_time = str(show_time)
#     d.replace(day=show_time.day, year=show_time.year, month=show_time.month)
#     t.replace(hour=show_time.hour, minute=show_time.minute)
#     print(d, t, show_time)
#     # st.rerun()
# if row2_1[1].button("Tiếp"):
#     print("Next")
#     print(show_time)
#     show_time = show_time + pd.to_timedelta(15, unit='m')
#     st.session_state.show_time = str(show_time)
#     d.replace(day=show_time.day, year=show_time.year, month=show_time.month)
#     t.replace(hour=show_time.hour, minute=show_time.minute)

#     print(d, t, show_time)
#     # st.rerun()

def draw_plotly(y_name, y_max, y_min):
    
    if y_name in ["MST_act", "HRHT_act"]:
        y_max = 545
        y_min = 530

    show_df = df

    # print("draw_plotly", d, t, show_time)
    max_time = pd.to_datetime(str(d) + " " + str(t))
    # max_time = show_time
    min_time = max_time - pd.to_timedelta(12, unit='H')

    # print(min_time, max_time)
    show_df = df[(df["DateTime"]>=min_time) & (df["DateTime"]<=max_time + pd.to_timedelta(3, unit='H'))]

    show_df_pred = df_pred[df_pred['DateTime']==max_time]

    fig = go.Figure()

    x = show_df['DateTime'].to_list()
    y = show_df[y_name].to_list()
    fig.add_trace(go.Scatter(
        x=x, y=y,
        line_color='rgb(30, 30, 186)',
        name=y_name,
    ))
    tmp_df = df[y_name].describe()

    # x_pred = list(pd.date_range(np.max(x), periods=36+1, freq="5min"))
    # y_pred = list(list([y[-1]])+[y[random.randint(0, len(y)-1)] + (1-random.randint(0, 2))*tmp_df['std'] for i in range(36)])
    x_pred = [max_time]+show_df_pred['DateTimePrediction'].to_list()
    y_pred = show_df[show_df['DateTime']==max_time][y_name].to_list()+show_df_pred[y_name+"_predict"].to_list()

    print(tmp_df)
    y_upper = [val + 1*tmp_df['std'] for val in y_pred]
    y_lower = [val - 1*tmp_df['std'] for val in y_pred]

    fig.add_trace(go.Scatter(
        x=x_pred+x_pred[::-1],
        y=y_upper+y_lower[::-1],
        fill='toself',
        fillcolor='rgba(252, 132, 3,0.2)',
        line_color='rgba(255,255,255,0)',
        showlegend=False,
        name=y_name+"_bound",
    ))

    fig.add_trace(go.Scatter(
        x=x_pred, y=y_pred,
        line_color='rgb(252, 132, 3)',
        name=y_name+" dự đoán",
    ))
    fig.add_vline(x=x_pred[0], line_width=3, line_dash="dash", line_color="green", name="Thời điểm hiện tại", showlegend=True)
    if y_max is not None:
        fig.add_hline(y=y_max, name="Ngưỡng trên", line_dash="dash", showlegend=True, line_color='rgb(212, 23, 74)')
    if y_min is not None:
        fig.add_hline(y=y_min, name="Ngưỡng dưới", line_dash="dash", showlegend=True, line_color='rgb(212, 23, 74)')

    fig.update_traces(mode='lines')
    fig.update_layout(
        margin={'t':20,'l':0,'b':0,'r':0},
        legend=dict(
            orientation="h",
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        ),
        xaxis_title="Thời gian",
        yaxis_title="Nhiệt độ (°C)",
        title=dict(text=f"Biểu đồ dự đoán {y_name} theo thời gian", font=dict(size=15), automargin=True, yref='paper')

    )
    return fig


st.plotly_chart(draw_plotly(option, None, None), use_container_width=True)

# while True:
#     sleep(5)
#     st.rerun()