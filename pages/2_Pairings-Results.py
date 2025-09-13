import pandas as pd
import numpy as np
import random as rm
import streamlit as st
import datetime as dt
from shared_library import *


st.set_page_config(
    page_title="Tennis Open",
    page_icon="EGVOpenLogo.ico",
    layout="wide",
    initial_sidebar_state="expanded"
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

# Hide Streamlit menu and footer
hide_streamlit_style = """
        <style>
        .stToolbarActions {display: none !important;}
        </style>
        """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)


#st.sidebar.markdown("<BR>",unsafe_allow_html=True)
#image_html = rounded_image_html("Sponsor.jpg", 300)
#st.sidebar.markdown(image_html, unsafe_allow_html=True)

@st.cache_data()
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')


logo, heading, buf = st.columns((3,10,3),vertical_alignment="top")
logo.image("EGVOpenLogo.png", width=100)
heading.markdown('<p style="font-size:44px;font-weight: bold;text-align:center;vertical-align:middle;color:blue;margin:0px;padding:0px">Match Results</p>', unsafe_allow_html=True)
st.markdown('<BR>', unsafe_allow_html=True)
st.markdown('<BR>', unsafe_allow_html=True)

df=Load_MatchResults()
players = Load_Players()

round = int(df['Round#'].max())

if round != round:
    round = 1

display_cols = ['Match#','Player1 Name','Player2 Name','Schedule Date', 'Schedule Time','Match Score','Winner','Status']

tab_titles = [f"Round {i}" for i in range(1, round + 1)]
tabs = st.tabs(tab_titles)

for i, tab in enumerate(tabs, start=1):
    with tab:
        st.markdown('<BR>', unsafe_allow_html=True)

        round_df = df[df['Round#'] == i]


        round_df['Schedule Date'] = round_df['Schedule Date'].dt.strftime('%d-%b-%y')


        html_txt = get_html_hyperlink_table(round_df[display_cols].fillna("--"),players,'Y')
        st.markdown(html_txt, unsafe_allow_html=True)


        csvfile = convert_df(round_df)

        download_file_name= f"EGV_Tennis_Round_{round}_Results.csv"
        st.markdown('<BR>',unsafe_allow_html=True)
        st.download_button(
                label="Download - CSV",
                data=csvfile,
                file_name=download_file_name,
                mime='text/csv',
                icon=":material/download:",
                key=f"Download_Results_{i}"
        )
