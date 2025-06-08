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




st.markdown('<p style="font-size:40px;font-weight: bold;text-align:center;vertical-align:middle;color:blue;margin:0px;padding:0px">Match Results</p>', unsafe_allow_html=True)
st.markdown('<BR>', unsafe_allow_html=True)
st.markdown('<BR>', unsafe_allow_html=True)
df=st.session_state.match_results
players = st.session_state.player_list

round = df['Round#'].max()

tab_titles = [f"Round {i}" for i in range(1, round + 1)]
tabs = st.tabs(tab_titles)

for i, tab in enumerate(tabs, start=1):
    with tab:
        st.markdown('<BR>', unsafe_allow_html=True)

        #st.write(f"### Round {i} Match Results")
        round_df = df[df['Round#'] == i]
        round_df.set_index('Match#', inplace=True)
        round_df['Won By'] = round_df['Winner'].apply(lambda x: players[x].name)

        html_txt = get_markdown_table(round_df[['Player1','Player2','Match_Result','Won By']])
        #st.write(html_txt)
        st.markdown(html_txt, unsafe_allow_html=True)
