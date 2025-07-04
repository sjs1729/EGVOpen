import pandas as pd
import numpy as np
import random as rm
import streamlit as st
from shared_library import *
import base64

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

# Styles we'll apply to images
img_style = """
    border: 2px solid #555;
    border-radius: 12px;
    padding: 4px;
    margin: 4px;
    max-width: 100%;
    height: auto;
"""


image_dir = "images/Match_Results/"


st.markdown('<p style="font-size:40px;font-weight: bold;text-align:center;vertical-align:middle;color:blue;margin:0px;padding:0px">Match Details</p>', unsafe_allow_html=True)
st.markdown('<BR>', unsafe_allow_html=True)


@st.cache_data()
def Initial_Player_List():
    df = pd.read_csv("PlayerList.csv")

    return df

initial_player_list = Initial_Player_List()


@st.cache_data()
def Load_Players():
    df = pd.read_csv("PlayerList.csv")
    players = []
    for i in df.index:
        id = i
        seed = df.loc[i,'Rank']
        name = df.loc[i,'Name']
        players.append(Player(id,name,seed=seed))

    return players

def Load_MatchResults():
    df = pd.read_csv("Match_Results.csv")

    # Convert 'Schedule_Date' to datetime (date only)
    df['Schedule Date'] = pd.to_datetime(df['Schedule Date'], format='%d-%b-%Y')

    # Convert 'Schedule_Time' to datetime.time
    df['Schedule Time'] = pd.to_datetime(df['Schedule Time'], format='%I:%M %p').dt.time

    # Optional: combine date and time into a single datetime column
    df['Scheduled_DateTime'] = df.apply(lambda row: pd.Timestamp.combine(row['Schedule Date'], row['Schedule Time']), axis=1)

    return df

def get_markdown_stat_table(data, header='Y', footer='N'):

    #st.write(data)
    if header == 'Y':

        cols = data.columns
        ncols = len(cols)
        if ncols < 5:
            html_script = "<table><style> table {border-collapse: collapse;width: 100%; border: 1px solid #ddd;}th {background-color: #ffebcc;padding:0px;} td {font-size='5px;text-align:center;padding:0px;'}tr:nth-child(even) {background-color: #f2f2f2;}</style><thead><tr style='width:100%;border:none;font-family:Courier; color:Red; font-size:14px'>"
        elif ncols < 8:
            html_script = "<table><style> table {border-collapse: collapse;width: 100%; border: 1px solid #ddd;}th {background-color: #ffebcc;padding:0px;} td {font-size='5px;text-align:center;padding:0px;'}tr:nth-child(even) {background-color: #f2f2f2;}</style><thead><tr style='width:100%;border:none;font-family:Courier; color:Red; font-size:12px'>"
        else:
            html_script = "<table><style> table {border-collapse: collapse;width: 100%; border: 1px solid #ddd;}th {background-color: #ffebcc;padding:0px;} td {font-size='5px;text-align:center;padding:0px;'}tr:nth-child(even) {background-color: #f2f2f2;}</style><thead><tr style='width:100%;border:none;font-family:Courier; color:Red; font-size:10px'>"


        for i in cols:
            if 'Fund' in i or 'Name' in i:
                html_script = html_script + "<th style='text-align:left'>{}</th>".format(i)
            else:
                html_script = html_script + "<th style='text-align:center;width:33.33%'>{}</th>".format(i)

    html_script = html_script + "</tr></thead><tbody>"
    for j in data.index:
        if ncols < 5:
            html_script = html_script + "<tr style='border:none;font-family:Courier; color:Blue; font-size:12px;padding:1px;';>"
        elif ncols < 8:
            html_script = html_script + "<tr style='border:none;font-family:Courier; color:Blue; font-size:11px;padding:1px;';>"
        else:
            html_script = html_script + "<tr style='border:none;font-family:Courier; color:Blue; font-size:9px;padding:1px;';>"

        a = data.loc[j]
        for k in cols:

            if '%' in a['Match Stats']:
                if k == 'Match Stats':
                    html_script = html_script + "<td style='padding:2px;text-align:center' rowspan='1'>{}</td>".format(a[k])
                else:
                    if a[k] == 100.0:
                        html_script = html_script + "<td style='padding:2px;text-align:center' rowspan='1'>{}</td>".format(int(a[k]))
                    else:
                        html_script = html_script + "<td style='padding:2px;text-align:center' rowspan='1'>{}</td>".format(a[k])

            else:
                if k == 'Match Stats':
                    html_script = html_script + "<td style='padding:2px;text-align:center' rowspan='1'>{}</td>".format(a[k])
                else:
                    html_script = html_script + "<td style='padding:2px;text-align:center' rowspan='1'>{}</td>".format(int(a[k]))


    html_script = html_script + '</tbody></table>'

    return html_script



match_results = Load_MatchResults()
df = match_results[match_results['Status'] == 'Completed'].sort_values("Match#")
df.set_index("Match#", inplace=True)


#p_standing = player_standings()

default_image_path = f"{image_dir}/default.jpg"

match_list = [f"{i}-{df.loc[i,'Player1 Name']} vs {df.loc[i,'Player2 Name']}" for i in df.index]
left, right = st.columns((5,6))

match_sel = left.selectbox("Select Match",match_list,0,label_visibility='collapsed')
left.write("  ")
match_no = int(match_sel.split("-")[0])
player1 = df.loc[match_no,'Player1 Name']
player2 = df.loc[match_no,'Player2 Name']
winner = df.loc[match_no,'Winner']
match_score = df.loc[match_no,'Match Score']

if winner == player1:
    html_text = f"""
<div style='text-align: center; font-size: 24px;'>
  <b>Winner: </b>  <b>{player1}</b><BR>
  <b><span style='color: #e74c3c'>{match_score}</span></b>
</div>
"""
else:
    html_text = f"""
<div style='text-align: center; font-size: 24px;'>
  <b>Winner: </b>  <b>{player2}</b><BR>
  <b><span style='color: #e74c3c'>{match_score}</span></b>
</div>
"""
right.markdown('<BR>',unsafe_allow_html=True)
right.write("  ")

right.markdown(html_text,unsafe_allow_html=True)
right.markdown('<BR>',unsafe_allow_html=True)



show_image = left.empty()

image_path = f"{image_dir}/{match_no}.jpg"

try:
    # Use HTML to control size
    show_image.image(image_path, width=600, output_format="PNG")
except:
    show_image.image(default_image_path, width=600, output_format="PNG")


df = pd.read_csv("MatchStat.csv")

player1_stat = {
                'Games Won':0,
                'Total Points Won':0,
                'Points Win %':0,
                'Aces':0,
                'Double Faults':0,
                'First Serve %':0.0,
                'First Serve Win %':0.0,
                'Second Serve %':0.0,
                'Second Serve Win %':0.0,
                'First Serves':0,
                'First Serve Wins':0,
                'First Serve Faults':0,
                'First Serve Loss':0,
                'Second Serves':0,
                'Second Serve Wins':0,
                'Second Serve Loss':0
                }

player2_stat = {
                'Games Won':0,
                'Total Points Won':0,
                'Points Win %':0,
                'Aces':0,
                'Double Faults':0,
                'First Serve %':0.0,
                'First Serve Win %':0.0,
                'Second Serve %':0.0,
                'Second Serve Win %':0.0,
                'First Serves':0,
                'First Serve Wins':0,
                'First Serve Faults':0,
                'First Serve Loss':0,
                'Second Serves':0,
                'Second Serve Wins':0,
                'Second Serve Loss':0
                }

df_match = df[df['Match#'] == match_no]

if len(df_match) < 1:
    st.warning("Stats Not Updated for this Match yet. Be patient")
    st.stop()

for _, row in df_match.iterrows():

    server = row['Server']
    receiver = row['Receiver']

    if player1 == server:
        if int(row['Total Points Won']) > int(row['Total Points Lost']):
            player1_stat['Games Won'] += 1
        else:
            player2_stat['Games Won'] += 1

        player1_stat['Total Points Won']  += int(row['Total Points Won'])
        player2_stat['Total Points Won']  += int(row['Total Points Lost'])
        player1_stat['First Serves'] += int(row['First Serves'])
        player1_stat['First Serve Wins'] += int(row['First Serve Wins'])
        player1_stat['First Serve Faults'] += int(row['First Service Fault'])
        player1_stat['First Serve Loss'] += int(row['First Serve Loss'])
        player1_stat['Second Serves'] += int(row['Second Serves'])
        player1_stat['Second Serve Wins'] += int(row['Second Serve Wins'])
        player1_stat['Second Serve Loss'] += int(row['Second Serve Loss'])
        player1_stat['Double Faults'] += int(row['Double Faults'])
        player1_stat['Aces'] += int(row['Aces'])


        #st.write(server,receiver,row['Total Points Won'], row['Total Points Lost'])

    elif player2 == server:

        if int(row['Total Points Won']) > int(row['Total Points Lost']):
            player2_stat['Games Won'] += 1
        else:
            player1_stat['Games Won'] += 1

        player2_stat['Total Points Won']  += int(row['Total Points Won'])
        player1_stat['Total Points Won']  += int(row['Total Points Lost'])
        player2_stat['First Serves'] += int(row['First Serves'])
        player2_stat['First Serve Wins'] += int(row['First Serve Wins'])
        player2_stat['First Serve Faults'] += int(row['First Service Fault'])
        player2_stat['First Serve Loss'] += int(row['First Serve Loss'])
        player2_stat['Second Serves'] += int(row['Second Serves'])
        player2_stat['Second Serve Wins'] += int(row['Second Serve Wins'])
        player2_stat['Second Serve Loss'] += int(row['Second Serve Loss'])
        player2_stat['Double Faults'] += int(row['Double Faults'])
        player2_stat['Aces'] += int(row['Aces'])



        #st.write(server,receiver,row['Total Points Won'], row['Total Points Lost'])



player1_stat['Points Win %'] = round(100 * player1_stat['Total Points Won']/ (player1_stat['Total Points Won'] + player2_stat['Total Points Won']),2)
player2_stat['Points Win %'] = round(100 * player2_stat['Total Points Won']/ (player1_stat['Total Points Won'] + player2_stat['Total Points Won']),2)

player1_stat['First Serve %'] = round(100*((player1_stat['First Serves'] - player1_stat['First Serve Faults'])/player1_stat['First Serves']),2)
player2_stat['First Serve %'] = round(100*((player2_stat['First Serves'] - player2_stat['First Serve Faults'])/player2_stat['First Serves']),2)

player1_stat['First Serve Win %'] = round(100*(player1_stat['First Serve Wins']/player1_stat['First Serves']),2)
player2_stat['First Serve Win %'] = round(100*(player2_stat['First Serve Wins']/player2_stat['First Serves']),2)

player1_stat['Second Serve %'] = round(100*((player1_stat['Second Serves'] - player1_stat['Double Faults'])/player1_stat['Second Serves']),2)
player2_stat['Second Serve %'] = round(100*((player2_stat['Second Serves'] - player2_stat['Double Faults'])/player2_stat['Second Serves']),2)

player1_stat['Second Serve Win %'] = round(100*(player1_stat['Second Serve Wins']/player1_stat['Second Serves']),2)
player2_stat['Second Serve Win %'] = round(100*(player2_stat['Second Serve Wins']/player2_stat['Second Serves']),2)


#st.dataframe(df_match)

stat_rec = []

display_stats = ['Games Won','Total Points Won','Points Win %','Aces','Double Faults','First Serve %','First Serve Win %',
                 'Second Serve %','Second Serve Win %']

for stat in player1_stat:

    if stat in display_stats:
        values = player1_stat[stat],stat,player2_stat[stat]
        stat_rec.append(values)


stat_df = pd.DataFrame(stat_rec, columns=[player1,'Match Stats',player2])

html_text = get_markdown_stat_table(stat_df)
#st.write(html_text)
right.markdown(html_text, unsafe_allow_html=True)



#st.markdown(html_text, unsafe_allow_html=True)
