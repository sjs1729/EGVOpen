import pandas as pd
import numpy as np
import random as rm
import streamlit as st
from shared_library import *


st.set_page_config(
    page_title="Tennis Open",
    page_icon="tennis_open.ico",
    layout="wide"
    )


st.markdown(
    """
    <style>
    .block-container {
        padding-top: 2rem !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)




st.markdown('<p style="font-size:40px;font-weight: bold;text-align:center;vertical-align:middle;color:blue;margin:0px;padding:0px">Standings</p>', unsafe_allow_html=True)
st.markdown('<BR>', unsafe_allow_html=True)

display_cols=['Rank','Player Name','Matches Played','Wins#','Loses#','Points','TB1', 'TB2', 'TB3']

p_standing = player_standings()
p_standing['Rank']=p_standing['Rank'].apply(lambda x: int(x))

html_text = get_markdown_table(p_standing[display_cols])
st.markdown(html_text, unsafe_allow_html=True)
