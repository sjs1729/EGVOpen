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

def get_html_table(data, players):

    cols = data.columns


    ncols = len(cols)

    html_script = "<table><style> table {border-collapse: collapse;width: 100%; border: 1px solid #ddd;}th {background-color: #ffebcc;padding:0px;} td {font-size='5px;text-align:center;padding:0px;'}tr:nth-child(even) {background-color: #f2f2f2;}</style><thead><tr style='width:100%;border:none;font-family:Courier; color:Red; font-size:14px'>"

    for i in cols:
        html_script = html_script + "<th style='text-align:center''>{}</th>".format(i)

    html_script = html_script + "</tr></thead><tbody>"

    for j in data.index:


        html_script = html_script + "<tr style='border:none;font-family:Courier; color:Blue; font-size:14px;padding:1px;';>"
        a = data.loc[j]
        for k in cols:

            if k == 'Match#':
                match_url_link = "http://localhost:8501/Match_Stats?mid={}".format(a[k])
                html_script += "<td style='padding:2px; text-align:center' rowspan='1'><a href={} style='text-decoration:underline; color:blue;'>{}</a></td>".format(match_url_link,a[k])
            elif k == 'Against':
                player_id = get_player_id(a[k],players)
                player_url_link = "http://localhost:8501/Player_Stats?id={}".format(player_id)
                html_script += "<td style='padding:2px; text-align:center' rowspan='1'><a href={} style='text-decoration:underline; color:blue;'>{}</a></td>".format(player_url_link,a[k])
            else:
                html_script = html_script + "<td style='padding:2px;text-align:center' rowspan='1'>{}</td>".format(a[k])

    html_script = html_script + '</tbody></table>'

    return html_script


image_dir = "images"


st.markdown('<p style="font-size:40px;font-weight: bold;text-align:center;vertical-align:middle;color:blue;margin:0px;padding:0px">Player Stats</p>', unsafe_allow_html=True)
st.markdown('<BR>', unsafe_allow_html=True)


players = Load_Players()
param_id = st.query_params.get("id")

if param_id:
    def_id = int(param_id) - 1
else:
    def_id = 0

#st.write(players)


p_standing = player_standings()

default_image_path = f"{image_dir}/default.png"

p_list = [f"{x.id}-{x.name}" for x in players]
left,buf, right = st.columns((9,2,6))

show_image = right.empty()
player_sel = left.selectbox("Select Player",p_list,def_id,label_visibility='collapsed')
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
#st.write(matches_played)
left.markdown(get_markdown_col_fields("Matches Played", len(matches_played), format_amt = 'N'),unsafe_allow_html=True)
left.markdown(get_markdown_col_fields("Matches Won (Points)", players[p_id-1].points, format_amt = 'N'),unsafe_allow_html=True)
left.markdown(get_markdown_col_fields("Current Position", int(current_position), format_amt = 'N'),unsafe_allow_html=True)

st.markdown('<BR>', unsafe_allow_html=True)

match_hist_rec = []
for idx , row in matches_played.iterrows():

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

    values = rslt, opponent, match_score , round_no, match_no
    #values = rslt, match_score, opponent, opp_point, round_no
    match_hist_rec.append(values)

match_history = pd.DataFrame(match_hist_rec, columns=['Result','Against', 'Score','Round', 'Match#'])

if len(match_history) > 0:
    st.success(f"{players[p_id-1].name} - Match History")
    html_text = get_html_table(match_history, players)
    st.markdown(html_text, unsafe_allow_html=True)

#player_rank = player_standings()
#html_script = get_markdown_table(player_rank)
#st.markdown(html_script, unsafe_allow_html=True)
