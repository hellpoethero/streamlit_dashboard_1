import streamlit as st
import numpy as np
import pandas as pd
import datetime
from st_pages import show_pages_from_config, add_page_title
import plotly.graph_objects as go
import plotly.express as px
from utils import DataLoader

add_page_title(layout="wide")
show_pages_from_config()
state = st.session_state

df = DataLoader.load_full_data()
max_time = df["Time"].max()
min_time = df["Time"].max() - pd.to_timedelta(1, unit="d")

row = st.columns(4)
d = row[0].date_input(
    "Chọn khoảng thời gian",
    (max_time, max_time),
    df["Time"].min(),
    df["Time"].max(),
    format="MM/DD/YYYY",
    key="d",
)

option1 = row[1].selectbox(
    "Lựa chọn chỉ số 1", ["None"] + [col for col in df.columns if col != "Time"]
)
option2 = row[2].selectbox(
    "Lựa chọn chỉ số 2", ["None"] + [col for col in df.columns if col != "Time"]
)
option3 = row[3].selectbox(
    "Lựa chọn chỉ số 3", ["None"] + [col for col in df.columns if col != "Time"]
)
# option1 = "MST_act"
# option2 = "AHAGOT_act"
# option3 = "AHAGIT_act"

if len(d) == 2:
    show_df = df

    print(d)
    show_df = df[(df["Time"].dt.date >= d[0]) & (df["Time"].dt.date <= d[1])]

    print(show_df.shape)
    cols = []
    if option1 != "None":
        cols.append(option1)
    if option2 != "None":
        cols.append(option2)
    if option3 != "None":
        cols.append(option3)

    if len(cols) > 0:
        colors = ["#1170aa", "#fc7d0b", "#59A14F"]
        st.subheader("Thống kê chỉ số: " + ", ".join(cols))
        tab1, tab2, tab3 = st.tabs(["Thống kê dữ liệu", "Biểu đồ theo thời gian", "Chi tiết dữ liệu"])
        with tab1:
            tmp_df = show_df[cols].describe().transpose()
            st.dataframe(tmp_df, use_container_width=True)

            row = st.columns(3)

            for i in range(len(cols)):
                col = cols[i]

                fig = go.Figure()

                # fig_box = px.box(data_frame=show_df, y=col,width=800, height=400,
                #          line=dict(color=colors[i]))
                fig.add_trace(
                    go.Box(
                        y=show_df[col],
                        fillcolor=colors[i],
                        line=dict(color="black"),
                        name=col,
                    )
                )

                fig.update_layout(
                    margin={"t": 10, "l": 0, "b": 0, "r": 0},
                    legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
                    yaxis_title="Nhiệt độ (°C)",
                )
                row[i].plotly_chart(fig, use_container_width=True)

        with tab2:
            fig = go.Figure()

            for i in range(len(cols)):
                col = cols[i]
                x = show_df["Time"].to_list()
                y = show_df[col].values
                fig.add_trace(
                    go.Scatter(
                        x=x, y=y, line_color=colors[i], name=col, yaxis=f"y{i+1}"
                    )
                )

            fig.update_traces(mode="lines")

            fig.update_layout(
                margin={"t": 20, "l": 0, "b": 0, "r": 0},
                legend=dict(
                    yanchor="top", y=0.99, xanchor="left", x=0.01, orientation="h"
                ),
                xaxis=dict(domain=[0, 1 if len(cols) < 3 else 0.925]),
                yaxis=dict(
                    title=cols[0],
                    titlefont=dict(color=colors[0]),
                    tickfont=dict(color=colors[0]),
                ),
                xaxis_title="Thời gian",
                title=dict(
                    text=f"Biểu đồ {', '.join(cols)} theo thời gian",
                    font=dict(size=15),
                    automargin=True,
                    yref="paper",
                ),
            )

            if len(cols) >= 2:
                fig.update_layout(
                    yaxis2=dict(
                        title=cols[1],
                        titlefont=dict(color=colors[1]),
                        tickfont=dict(color=colors[1]),
                        # anchor="free",
                        overlaying="y",
                        side="right",
                        showgrid=True,
                    ),
                )
                fig["layout"]["yaxis2"]["showgrid"] = False
                
            if len(cols) >= 3:
                fig.update_layout(
                    yaxis3=dict(
                        title=cols[2],
                        titlefont=dict(color=colors[2]),
                        tickfont=dict(color=colors[2]),
                        # anchor="x",
                        overlaying="y",
                        side="right",
                        position=1,
                        showgrid=True,
                    ),
                )
                fig["layout"]["yaxis3"]["showgrid"] = False
                
            st.plotly_chart(fig, use_container_width=True)

        with tab3:
            st.dataframe(show_df[["Time"]+cols], use_container_width=True)