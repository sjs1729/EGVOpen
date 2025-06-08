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




st.markdown('<p style="font-size:40px;font-weight: bold;text-align:center;vertical-align:middle;color:blue;margin:0px;padding:0px">Player Details</p>', unsafe_allow_html=True)
st.markdown('<BR>', unsafe_allow_html=True)
df=st.session_state.match_results
players = st.session_state.player_list

p_standing = player_standings()

p_list = [f"{x.id}-{x.name}" for x in players]

player_sel = st.selectbox("Select Player",p_list,0)

p_id = int(player_sel.split("-")[0])


current_position = p_standing.loc[p_id,'Rank']



matches_played = df[(df['Id1']==p_id) | (df['Id2']==p_id)]

st.markdown(get_markdown_col_fields("Matches Played", len(matches_played), format_amt = 'N'),unsafe_allow_html=True)
st.markdown(get_markdown_col_fields("Matches Won (Points)", players[p_id].points, format_amt = 'N'),unsafe_allow_html=True)
st.markdown(get_markdown_col_fields("Current Position", int(current_position), format_amt = 'N'),unsafe_allow_html=True)

st.markdown('<BR>', unsafe_allow_html=True)

match_hist_rec = []
for _ , row in matches_played.iterrows():

    id_1 = row['Id1']
    id_2 = row['Id2']
    match_no = row['Match#']
    round_no = row['Round#']
    match_score = row['Match_Result']
    winner = row['Winner']

    if p_id == id_1:
        opp_id = id_2
    else:
        opp_id = id_1

    opponent = players[opp_id].name
    opp_point = players[opp_id].points

    if p_id == winner:
        rslt = "Won"
    else:
        rslt = "Lost"

    values = rslt, match_score, opponent, opp_point, round_no
    match_hist_rec.append(values)

match_history = pd.DataFrame(match_hist_rec, columns=['Result','Score','Opponent','Opponent Point','Round'])

if len(match_history) > 0:
    st.success("Match History")
    html_text = get_markdown_table(match_history)
    st.markdown(html_text, unsafe_allow_html=True)

#player_rank = player_standings()
#html_script = get_markdown_table(player_rank)
#st.markdown(html_script, unsafe_allow_html=True)
