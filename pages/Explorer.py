import streamlit as st
import pandas as pd
import altair as alt
import plotly.graph_objects as go
import numpy as np
import datetime
from st_pages import show_pages_from_config, add_page_title
from pygwalker.api.streamlit import StreamlitRenderer
from utils import DataLoader

add_page_title(layout="wide")
show_pages_from_config()
state = st.session_state

df = DataLoader.load_full_data()
pyg_app = StreamlitRenderer(df)
 
pyg_app.explorer()