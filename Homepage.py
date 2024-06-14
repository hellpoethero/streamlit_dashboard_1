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


def show_metrics(show_df, current_time):
    cols = st.columns([2,1,1,1,1,1])
    cols[0].metric("Thời điểm hiển thị dữ liệu", str(current_time))
    cols[1].metric("HR effect", str(int(show_df["hr"].values[-1])))
    cols[2].metric("Nhiệt độ hơi chính", str(int(show_df["MST_act"].values[-1])) + " °C" )
    cols[3].metric("Nhiệt độ hơi tái nhiệt", str(int(show_df["HRHT_act"].values[-1])) + " °C")
    # cols[3].metric("Nhiệt độ khói vào AHA", str(int(show_df["AHAGIT_act"].values[-1])) + " °C", "4%")
    # cols[4].metric("Nhiệt độ khói vào AHB", str(int(show_df["AHBGIT_act"].values[-1])) + " °C", "4%")
    cols[4].metric("Nhiệt độ khói ra AHA", str(int(show_df["AHAGOT_act"].values[-1])) + " °C")
    cols[5].metric("Nhiệt độ khói ra AHB", str(int(show_df["AHBGOT_act"].values[-1])) + " °C")

df, df_pred = DataLoader.load_prediction()
show_df = df

df_soot = DataLoader.load_sootblow()

max_time = df['DateTime'].max()
min_time = df['DateTime'].max() - pd.to_timedelta(12, unit='H')
show_df = df[(df["DateTime"]>=min_time) & (df["DateTime"]<=max_time)]

show_df_pred = df_pred[df_pred['DateTime']==max_time]

st.subheader("Cảnh báo")
st.warning(":red[Nhiệt độ khói thoát AHB đang vượt ngưỡng]")
st.warning(":red[Đã 48 tiếng từ lần thổi bụi cuối cùng]")

st.subheader("Thông số")
# st.text(str(max_time))
show_metrics(show_df, max_time)

st.subheader("Thống kê thổi bụi")
cols = st.columns([3,6,3])

cols[0].caption("Khu vực thổi")
cols[0].text("2")
cols[0].text("3")

cols[1].caption("Thời điểm thổi gần nhất")
g2_lastest = df_soot[(df_soot['start_datetime']==df_soot[df_soot['group']==2]['start_datetime'].max()) & (df_soot['group']==2)]
g3_lastest = df_soot[(df_soot['start_datetime']==df_soot[df_soot['group']==3]['start_datetime'].max()) & (df_soot['group']==3)]

cols[1].text(str(g2_lastest['start_datetime'].max()) + " - " + str(g2_lastest['finish_datetime'].max()))
cols[1].text(str(g3_lastest['start_datetime'].max()) + " - " + str(g3_lastest['finish_datetime'].max()))

cols[2].caption("Số vòi sử dụng")
cols[2].text("10")
cols[2].text("10")

def draw_plotly(y_name, y_max, y_min):

    fig = go.Figure()

    x = show_df['DateTime'].to_list()
    y = show_df[y_name].to_list()
    fig.add_trace(go.Scatter(
        x=x, y=y,
        line_color='rgb(30, 30, 186)',
        name=y_name,
    ))
    tmp_df = show_df[y_name].describe()

    # x_pred = list(pd.date_range(np.max(x), periods=36+1, freq="5min"))
    # y_pred = list(list([y[-1]])+[y[random.randint(0, len(y)-1)] + (1-random.randint(0, 2))*tmp_df['std'] for i in range(36)])
    x_pred = x[-1:]+show_df_pred['DateTimePrediction'].to_list()
    y_pred = y[-1:]+show_df_pred[y_name+"_predict"].to_list()
    y_upper = [val + tmp_df['std'] for val in y_pred]
    y_lower = [val - tmp_df['std'] for val in y_pred]

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
        margin={'t':50,'l':0,'b':0,'r':0},
        legend=dict(
            orientation="h",
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        ),
        xaxis_title="Thời gian",
        yaxis_title="Nhiệt độ (°C)",
        title=dict(text=f"Biểu đồ dự đoán {y_name} theo thời gian", font=dict(size=15), x=0.5, yref='paper',
        xanchor='center',
        yanchor= 'top')

    )
    return fig


st.plotly_chart(draw_plotly("hr", None, None), use_container_width=True)
st.plotly_chart(draw_plotly("MST_act", 545, 530), use_container_width=True)
st.plotly_chart(draw_plotly("HRHT_act", 545, 530), use_container_width=True)
# st.plotly_chart(draw_plotly("AHAGIT_act", None, None), use_container_width=True)
# st.plotly_chart(draw_plotly("AHBGIT_act", None, None), use_container_width=True)
st.plotly_chart(draw_plotly("AHAGOT_act", 124, None), use_container_width=True)
st.plotly_chart(draw_plotly("AHBGOT_act", 124, None), use_container_width=True)

# row1 = st.columns(2)
# row1[0].subheader("Nhiệt độ hơi chính")
# row1[0].line_chart(show_df, x="Time", y=["MST_act"], color=["#FF0000"])

# row1[1].subheader("Nhiệt độ hơi tái nhiệt")
# row1[1].line_chart(show_df, x="Time", y=["HRHT_act"], color=["#FF0000"])

# row2 = st.columns(2)
# row2[0].subheader("Nhiệt độ khói vào AHA")
# row2[0].line_chart(show_df, x="Time", y=["AHAGIT_act"], color=["#FF0000"])
# row2[1].subheader("Nhiệt độ khói vào AHB")
# row2[1].line_chart(show_df, x="Time", y=["AHBGIT_act"], color=["#FF0000"])

# row3 = st.columns(2)
# row3[0].subheader("Nhiệt độ khói ra AHA")
# row3[0].line_chart(show_df, x="Time", y=["AHAGOT_act"], color=["#FF0000"])
# row3[1].subheader("Nhiệt độ khói ra AHB")
# row3[1].line_chart(show_df, x="Time", y=["AHBGOT_act"], color=["#FF0000"])


