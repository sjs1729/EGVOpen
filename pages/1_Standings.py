import pandas as pd
import numpy as np
import random as rm
import streamlit as st
from shared_library import *
import os


st.set_page_config(
    page_title="Tennis Open",
    page_icon="tennis_open.ico",
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


def get_tournament_status():
    df = Load_MatchResults()

    nrows = len(df)

    round = 1

    if nrows > 0:
        round = df['Round#'].max()


    return round

st.markdown('<p style="font-size:40px;font-weight: bold;text-align:center;vertical-align:middle;color:blue;margin:0px;padding:0px">Current Standings</p>', unsafe_allow_html=True)
st.markdown('<BR>', unsafe_allow_html=True)

nRound = get_tournament_status()

display_cols=['Rank','Player Name','Matches Played','Wins#','Loses#','Points','TB1', 'TB2', 'TB3']

p_standing = player_standings(1)
p_standing['Rank']=p_standing['Rank'].apply(lambda x: int(x))


html_text = get_markdown_table(p_standing[display_cols].sort_values(['Rank','Player Name']))
#st.write(html_text)
st.markdown(html_text, unsafe_allow_html=True)

csvfile = convert_df(p_standing[display_cols])

download_file_name= f"EGV_Tennis_{nRound}_Standings.csv"
st.markdown('<BR>',unsafe_allow_html=True)
st.download_button(
        label="Download CSV",
        data=csvfile,
        file_name=download_file_name,
        mime='text/csv',
        icon=":material/download:",
        key=f"Download_Standings"
)




#player_rank = player_standings()
#html_script = get_markdown_table(player_rank)
#st.markdown(html_script, unsafe_allow_html=True)
