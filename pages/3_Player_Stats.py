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

# Styles we'll apply to images
img_style = """
    border: 2px solid #555;
    border-radius: 12px;
    padding: 4px;
    margin: 4px;
    max-width: 100%;
    height: auto;
"""


image_dir = "images"


st.markdown('<p style="font-size:40px;font-weight: bold;text-align:center;vertical-align:middle;color:blue;margin:0px;padding:0px">Player Details</p>', unsafe_allow_html=True)
st.markdown('<BR>', unsafe_allow_html=True)


players = Load_Players()

#st.write(players)


p_standing = player_standings()

default_image_path = f"{image_dir}/default.png"

p_list = [f"{x.id}-{x.name}" for x in players]
left,buf, right = st.columns((9,2,6))

show_image = right.empty()
player_sel = left.selectbox("Select Player",p_list,0,label_visibility='collapsed')
#left.write("  ")
#left.write(player_sel)
p_id = int(player_sel.split("-")[0])
#p_last_name = player_sel.split("-")[1].split()[1]

image_path = f"{image_dir}/{p_id}.png"

try:
    show_image.image(image_path, width=200, output_format="PNG")
except:
    show_image.image(default_image_path, width=200, output_format="PNG")




current_position = p_standing.loc[p_id,'Rank']

df = Load_MatchResults()
df=df[df['Status'] == 'Completed']

matches_played = df[(df['Player1#']==p_id) | (df['Player2#']==p_id)]

left.markdown(get_markdown_col_fields("Matches Played", len(matches_played), format_amt = 'N'),unsafe_allow_html=True)
left.markdown(get_markdown_col_fields("Matches Won (Points)", players[p_id-1].points, format_amt = 'N'),unsafe_allow_html=True)
left.markdown(get_markdown_col_fields("Current Position", int(current_position), format_amt = 'N'),unsafe_allow_html=True)

st.markdown('<BR>', unsafe_allow_html=True)

match_hist_rec = []
for _ , row in matches_played.iterrows():

    id_1 = row['Player1#']
    id_2 = row['Player2#']
    match_no = row['Match#']
    round_no = row['Round#']
    match_score = row['Match Score']
    winner = row['Winner_Id']

    #st.write(id_1,id_2, p_id, winner)

    if p_id == id_1:
        opp_id = id_2
    else:
        opp_id = id_1

    opponent = players[int(opp_id)-1].name
    opp_point = players[int(opp_id)-1].points

    if p_id == winner:
        rslt = "Won"
    else:
        rslt = "Lost"

    values = rslt, opponent, match_score , round_no
    #values = rslt, match_score, opponent, opp_point, round_no
    match_hist_rec.append(values)

match_history = pd.DataFrame(match_hist_rec, columns=['Result','Against', 'Score','Round'])

if len(match_history) > 0:
    st.success(f"{players[p_id-1].name} - Match History")
    html_text = get_markdown_table(match_history)
    st.markdown(html_text, unsafe_allow_html=True)

#player_rank = player_standings()
#html_script = get_markdown_table(player_rank)
#st.markdown(html_script, unsafe_allow_html=True)
