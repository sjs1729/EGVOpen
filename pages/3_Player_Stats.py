import pandas as pd
import numpy as np
import random as rm
import streamlit as st
from shared_library import *


st.set_page_config(
    page_title="EGV Tennis Open",
    page_icon="EGVOpenLogo.ico",
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

# Custom CSS
st.markdown("""
    <style>
    .block-container {
        padding-top: 2rem !important;
        padding-left: 1rem;
        padding-right: 1rem;
    }
    table {
        border-collapse: collapse;
        width: 100%;
        border: 1px solid #ddd;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    th, td {
        padding: 10px;
        text-align: center;
        font-size: 14px;
    }
    th {
        background-color: #ffebcc;
        font-weight: bold;
    }
    tr:nth-child(even) {
        background-color: #f9f9f9;
    }
    .title {
        font-size: 36px;
        font-weight: bold;
        text-align: center;
        color: #004d99;
        margin-bottom: 20px;
    }
    .stat-box {
        padding: 16px;
        border-radius: 12px;
        background-color: #f0f8ff;
        box-shadow: 0 2px 6px rgba(0,0,0,0.1);
        margin-bottom: 10px;
    }
    @media screen and (max-width: 768px) {
        .block-container {
            padding: 0.5rem;
        }
        .title {
            font-size: 28px;
        }
        th, td {
            font-size: 12px;
            padding: 6px;
        }
        .stat-box {
            padding: 10px;
        }
    }
    </style>
""", unsafe_allow_html=True)

st.sidebar.markdown("<BR>",unsafe_allow_html=True)
image_html = rounded_image_html("Sponsor.jpg", 300)
st.sidebar.markdown(image_html, unsafe_allow_html=True)


st.cache_data()
def Load_MatchStats():
    df = pd.read_csv("MatchStat.csv")

    return df

def get_html_table(data, players):

    cols = data.columns


    ncols = len(cols)

    html_script = "<table><style> table {border-collapse: collapse;width: 100%; border: 1px solid #ddd;}th {background-color: #ffebcc;padding:0px;} td {font-size='5px;text-align:center;padding:0px;'}tr:nth-child(even) {background-color: #f2f2f2;}</style><thead><tr style='width:100%;border:none;font-family:Courier; color:Red; font-size:14px'>"

    for i in cols:
        html_script = html_script + "<th style='text-align:center''>{}</th>".format(i)

    html_script = html_script + "</tr></thead><tbody>"

    for j in data.index:


        html_script = html_script + "<tr style='border:none;font-family:Courier; color:#0866FF;font-weight:bold;font-size:14px;padding:1px;';>"
        a = data.loc[j]
        for k in cols:

            if k == 'Match#':
                match_url_link = "http://localhost:8501/Match_Stats?mid={}".format(a[k])
                html_script += "<td style='padding:2px; text-align:center' rowspan='1'><a href={} style='text-decoration:underline;font-weight:bold;color:#0866FF;'>{}</a></td>".format(match_url_link,a[k])
            elif k == 'Against':
                player_id = get_player_id(a[k],players)
                player_url_link = "http://localhost:8501/Player_Stats?id={}".format(player_id)
                html_script += "<td style='padding:2px; text-align:center' rowspan='1'><a href={} style='text-decoration:underline;font-weight:bold;color:#0866FF;'>{}</a></td>".format(player_url_link,a[k])
            else:
                html_script = html_script + "<td style='padding:2px;text-align:center' rowspan='1'>{}</td>".format(a[k])

    html_script = html_script + '</tbody></table>'

    return html_script

@st.cache_data()
def get_markdown_stat_table(df):

    html = """
                <style>
                table, tr, td {
                        border: none !important;
                        border-collapse: collapse;
                    }
                </style>
            """

    html += "<div style='font-size: 16px;font-family:sans-serif;color: #2C64F6;width: 100%; max-width: 800px;'><table style='width: 100%;'><tbody>"
    for _, row in df.iterrows():
        stat = str(row[0]).strip()
        value = str(row[1]).strip()
        html = html +  f"<tr style='backgroundColor:#ffffff'><td style='padding: 4px 8px; text-align: left; font-weight: 600;border:3 px solid #2C64F6;'>{stat}</td>"
        html = html +  f"<td style='padding: 4px 8px; text-align: center; font-weight: 400; font-family: sans-serif, monospace;border:3 px solid #FF64F6;'>{value} </td></tr>"
    html += "</tbody></table></div>"
    #st.write(html)
    return html



@st.cache_data()
def get_match_stat(player_name,df_match, stat_arr):

    player_stat = { 'Current Rank':stat_arr[0],
                    'Matches Played':stat_arr[1],
                    'Matches Won':stat_arr[2],
                    'Games Won':0,
                    'Games Lost':0,
                    'Aces':0,
                    'Double Faults':0,
                    'Points Won':0,
                    'Points Lost':0,
                    'Points Won (Win%) Lost':0,
                    'Points Won Serving':0,
                    'Points Lost Serving':0,
                    'Points Won Receiving':0,
                    'Points Lost Receiving':0,
                    'Points Won (Win%) Lost - Serving':0,
                    'Points Won (Win%) Lost - Receiving':0,
                    'First Serves':0,
                    'First Serve Wins':0,
                    'First Serve Loss':0,
                    'First Serve Faults':0,
                    'Second Serves':0,
                    'Second Serve Wins':0,
                    'Second Serve Loss':0,
                    'First Serve %':0.0,
                    'First Serve Win %':0.0,
                    'Second Serve %':0.0,
                    'Second Serve Win %':0.0,
                    }



    for _, row in df_match.iterrows():

        server = row['Server']
        receiver = row['Receiver']
        if player_name == server:



            if int(row['Game#']) < 13:
                if int(row['Total Points Won']) > int(row['Total Points Lost']):
                    player_stat['Games Won'] += 1
                else:
                    player_stat['Games Lost'] += 1




            #player1_stat['Points won Serving']  += int(row['Total Points Won'])
            player_stat['Points Won Serving'] += int(row['Total Points Won'])
            player_stat['Points Lost Serving'] += int(row['Total Points Lost'])

            player_stat['First Serves'] += int(row['First Serves'])
            player_stat['First Serve Wins'] += int(row['First Serve Wins'])
            player_stat['First Serve Faults'] += int(row['First Service Fault'])
            player_stat['Second Serves'] += int(row['Second Serves'])
            player_stat['Second Serve Wins'] += int(row['Second Serve Wins'])
            player_stat['Double Faults'] += int(row['Double Faults'])
            player_stat['Aces'] += int(row['Aces'])


            #st.write(server,receiver,row['Total Points Won'], row['Total Points Lost'],player_stat['Points Won Serving'],player_stat['Points Lost Serving'])

        elif player_name == receiver:

            if int(row['Game#']) < 13:
                if int(row['Total Points Won']) > int(row['Total Points Lost']):
                    player_stat['Games Lost'] += 1
                else:
                    player_stat['Games Won'] += 1



            player_stat['Points Won Receiving'] += int(row['Total Points Lost'])
            player_stat['Points Lost Receiving'] += int(row['Total Points Won'])




            #st.write(server,receiver,row['Total Points Won'], row['Total Points Lost'],player_stat['Points Won Receiving'],player_stat['Points Lost Receiving'])


    player_stat['Points Won'] = player_stat['Points Won Serving'] + player_stat['Points Won Receiving']
    player_stat['Points Lost'] = player_stat['Points Lost Serving'] + player_stat['Points Lost Receiving']
    #st.write(player_stat['Points Won'],player_stat['Points Lost'])
    temp_value = round(100 * player_stat['Points Won']/ (player_stat['Points Won'] + player_stat['Points Lost']),2)
    player_stat['Points Won (Win%) Lost'] = f"{player_stat['Points Won']} ({temp_value}%) {player_stat['Points Lost']}"

    #st.write(player_stat['Points Won %'])

    temp_value = round(100 * player_stat['Points Won Serving']/ (player_stat['Points Won Serving'] + player_stat['Points Lost Serving']),2)
    player_stat['Points Won (Win%) Lost - Serving'] = f"{player_stat['Points Won Serving']} ({temp_value}%) {player_stat['Points Lost Serving']}"


    temp_value = round(100 * player_stat['Points Won Receiving']/ (player_stat['Points Won Receiving'] + player_stat['Points Lost Receiving']),2)
    player_stat['Points Won (Win%) Lost - Receiving'] = f"{player_stat['Points Won Receiving']} ({temp_value}%) {player_stat['Points Lost Receiving']}"


    temp_value = round(100*((player_stat['First Serves'] - player_stat['First Serve Faults'])/player_stat['First Serves']),2)
    player_stat['First Serve %'] = f"{player_stat['First Serves']} ({temp_value}%)"


    temp_value = round(100*(player_stat['First Serve Wins']/player_stat['First Serves']),2)
    player_stat['First Serve Win %'] = f"{player_stat['First Serve Wins']} ({temp_value}%)"


    if player_stat['Second Serves'] != 0:
        temp_value = round(100*((player_stat['Second Serves'] - player_stat['Double Faults'])/player_stat['Second Serves']),2)
        player_stat['Second Serve %'] = f"{player_stat['Second Serves']} ({temp_value}%)"

        temp_value = round(100*(player_stat['Second Serve Wins']/player_stat['Second Serves']),2)
        player_stat['Second Serve Win %'] = f"{player_stat['Second Serve Wins']} ({temp_value}%)"

    else:
        temp_value = "NA"
        player_stat['Second Serve %'] = f"{player_stat['Second Serves']} ({temp_value}%)"
        player_stat['Second Serve Win %'] = f"{player_stat['Second Serve Wins']} ({temp_value}%)"



    #st.write(player_stat)

    #st.dataframe(df_match)

    stat_rec = []

    display_stats = ['Current Rank', 'Matches Played', 'Matches Won','Games Won','Games Lost','Points Won (Win%) Lost',
                     'Points Won (Win%) Lost - Serving', 'Points Won (Win%) Lost - Receiving','Aces','Double Faults',
                     'First Serve %','First Serve Win %','Second Serve %','Second Serve Win %']

    for stat in player_stat:

        if stat in display_stats:
            if stat != 'Tie Break Score':
                values = stat,player_stat[stat]
                stat_rec.append(values)
            else:
                if player_stat[stat] > 0:
                    values = stat,player_stat[stat]
                    stat_rec.append(values)


    stat_df = pd.DataFrame(stat_rec, columns=['Match Stats','Player'])

    #st.write(stat_df)

    return stat_df

image_dir = "images"


logo, heading, buf = st.columns((3,10,3),vertical_alignment="top")
logo.image("EGVOpenLogo.png", width=100)
heading.markdown('<p style="font-size:44px;font-weight: bold;text-align:center;vertical-align:middle;color:blue;margin:0px;padding:0px">Player Stats</p>', unsafe_allow_html=True)
st.markdown('<BR><BR>', unsafe_allow_html=True)


players = Load_Players()
param_id = st.query_params.get("id")

if param_id:
    def_id = int(param_id) - 1
else:
    def_id = 0



p_standing = player_standings()

default_image_path = f"{image_dir}/default.png"

p_list = [f"{x.id}-{x.name}" for x in players]
left,buf, right = st.columns((6,1,5))



player_sel = left.selectbox("Select Player",p_list,def_id,label_visibility='collapsed')
left.write("  ")
#left.write(player_sel)
p_id = int(player_sel.split("-")[0])
#p_last_name = player_sel.split("-")[1].split()[1]

right.markdown('<BR><BR>', unsafe_allow_html=True)
show_image = right.empty()
show_player_stat = left.empty()

image_path = f"{image_dir}/{p_id}.png"

try:
    show_image.image(image_path, width=250, output_format="PNG")
except:
    show_image.image(default_image_path, width=300, output_format="PNG")




current_position = p_standing.loc[p_id,'Rank']
matches_played = p_standing.loc[p_id,'Matches Played']
matches_won = p_standing.loc[p_id,'Wins#']

stat_arr = [current_position, matches_played,matches_won]


df = Load_MatchResults()
df=df[df['Status'] == 'Completed']

matches_played = df[(df['Player1#']==p_id) | (df['Player2#']==p_id)]
match_list = [int(i) for i in matches_played['Match#'].unique()]

df_stat = Load_MatchStats()
df_match_stat = df_stat[df_stat['Match#'].isin(match_list)]

df_all_match_stats = get_match_stat(players[p_id-1].name,df_match_stat,stat_arr)


#st.write(get_markdown_stat_table(df_all_match_stats))



show_player_stat.markdown(get_markdown_stat_table(df_all_match_stats), unsafe_allow_html=True)


#st.write(df_all_match_stats)
#left.markdown(get_markdown_col_fields("Matches Played", len(matches_played), format_amt = 'N'),unsafe_allow_html=True)
#left.markdown(get_markdown_col_fields("Matches Won (Points)", players[p_id-1].points, format_amt = 'N'),unsafe_allow_html=True)
#left.markdown(get_markdown_col_fields("Current Position", int(current_position), format_amt = 'N'),unsafe_allow_html=True)



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
    html_text = get_html_table(match_history, players)
    st.write("------------")
    if st.toggle("Match History", value=True):
        st.markdown(html_text, unsafe_allow_html=True)

#player_rank = player_standings()
#html_script = get_markdown_table(player_rank)
