import pandas as pd
import numpy as np
import random as rm
import streamlit as st
from shared_library import *


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

st.markdown("""
    <style>
      #MainMenu {visibility: hidden;}
      footer {visibility: hidden;}
      header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)


st.markdown('<p style="font-size:40px;font-weight: bold;text-align:center;vertical-align:middle;color:blue;margin:0px;padding:0px">EGV Tennis Open - 2025</p>', unsafe_allow_html=True)

left,centre, right = st.columns((1,10,1))
centre.image("images/EGV_TL.jpeg", width=1000)

@st.cache_data()
def Initial_Player_List():
    df = pd.read_csv("PlayerList.csv")


    return df

initial_player_list = Initial_Player_List()







st.markdown('<BR><BR>',unsafe_allow_html=True)
#st.markdown(get_markdown_col_fields("No of Players",nPlayers),unsafe_allow_html=True)
#st.markdown(get_markdown_col_fields("Total Rounds to be Played",tot_rounds),unsafe_allow_html=True)
#st.markdown(get_markdown_col_fields("Total Rounds to be Played",how_many_rounds(nPlayers)),unsafe_allow_html=True)
#st.markdown('<BR>', unsafe_allow_html=True)

match_results = Load_MatchResults()

incomplete_status = ['Scheduled','Re-Scheduled','Rain Delayed']

completed_matches = match_results[match_results['Status'] == 'Completed'].sort_values('Match#')
sched_matches = match_results[match_results['Status'].isin(incomplete_status)].sort_values('Scheduled_DateTime')

sched_match_cols = ['Match#','Round#','Player1 Name','Player2 Name','Scheduled Date','Schedule Time','Status']
completed_match_cols = ['Match#','Round#','Player1 Name','Player2 Name','Match Date','Match Score','Winner']

completed_matches['Match Date'] = pd.to_datetime(completed_matches['Schedule Date']).dt.strftime('%B %d')
sched_matches['Scheduled Date'] = pd.to_datetime(sched_matches['Schedule Date']).dt.strftime('%B %d')









tab1, tab2 = st.tabs(["Upcoming Matches","Completed Matches"])

with tab1:
    st.markdown('<BR>',unsafe_allow_html=True)

    html_txt = get_markdown_table(sched_matches[sched_match_cols])
    st.markdown(html_txt, unsafe_allow_html=True)

with tab2:
    st.markdown('<BR>',unsafe_allow_html=True)
    html_txt = get_markdown_table(completed_matches[completed_match_cols])
    st.markdown(html_txt, unsafe_allow_html=True)
