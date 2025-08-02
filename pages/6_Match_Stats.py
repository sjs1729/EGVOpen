import pandas as pd
import numpy as np
import random as rm
import streamlit as st
from shared_library import *
import base64
import google.generativeai as genai

st.set_page_config(
    page_title="EGV Tennis Open",
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

st.sidebar.markdown("<BR>",unsafe_allow_html=True)
image_html = rounded_image_html("Sponsor.jpg", 300)
st.sidebar.markdown(image_html, unsafe_allow_html=True)


logo, heading, buf = st.columns((3,10,3),vertical_alignment="top")
logo.image("EGVOpenLogo.png", width=100)
heading.markdown('<p style="font-size:44px;font-weight:bold;text-align:center;vertical-align:middle;color:color:#2C64F6;margin:0px;padding:0px">Match Details</p>', unsafe_allow_html=True)
st.markdown('<BR><BR>', unsafe_allow_html=True)


@st.cache_data()
def Initial_Player_List():
    df = pd.read_csv("PlayerList.csv")

    return df

initial_player_list = Initial_Player_List()




#st.cache_data()
def Load_MatchStats():
    df = pd.read_csv("MatchStat.csv")

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
            html_script = html_script + "<tr style='border:none;font-family:Courier;font-weight:550;color:#2C64F6; font-size:13px;padding:1px;';>"
        elif ncols < 8:
            html_script = html_script + "<tr style='border:none;font-family:Courier; font-weight:600;color:#2C64F6; font-size:11px;padding:1px;';>"
        else:
            html_script = html_script + "<tr style='border:none;font-family:Courier; font-weight:bold;color:#2C64F6; font-size:9px;padding:1px;';>"

        a = data.loc[j]
        for k in cols:
            html_script = html_script + "<td style='padding:2px;text-align:center' rowspan='1'>{}</td>".format(a[k])


    html_script = html_script + '</tbody></table>'

    return html_script


@st.cache_data()
def get_commentary(stat_df):

    API_KEY = "AIzaSyBjmmNJ76ZUosp68X30d6SGiaWZSJc-ov0"
    genai.configure(api_key=API_KEY)

    if 'stat_df' in locals() or 'stat_df' in globals():
        stat_df_string = stat_df.to_markdown(index=False)


        prompt = f"""
        You are a crowd captivating tennis match commentator
        Give me a commentary on the tennis match as data given and make it under 20 words as well as entertaining and humorous and dont humiliate any players and make it polite tone and prefereably dont add statistics.

        Match Data:
        {stat_df_string}

        Commentary:
        """

        try:
            model = genai.GenerativeModel('gemini-2.5-flash')
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            st.error(f"An error occurred: {e}")
            st.warning("Please ensure your API key is correct and you have network connectivity.")
    else:
        st.warning("`stat_df` is not defined. Please ensure the DataFrame is loaded or created before pressing the button.")

def get_match_comments(match_results, df_stat):
    for i in match_results.index:
        match_no = match_results.loc[i,'Match#']
        match_status = match_results.loc[i,'Status']
        match_cmnt = match_results.loc[i,'Match Commentary']
        p1 = match_results.loc[i,'Player1 Name']
        p2 = match_results.loc[i,'Player2 Name']
        df_match = df_stat[df_stat['Match#'] == match_no]


        if match_status == 'Completed' and match_cmnt != match_cmnt:
            if len(df_match) > 0:
                df_stat_1 = get_match_stat(p1, p2, df_match)
                commentary = get_commentary(df_stat_1)
                match_results.at[i,'Match Commentary'] = commentary
                st.write(p1,p2,commentary)


    match_results.to_csv("match_results_with_comments.csv",index=False)


@st.cache_data()
def get_match_stat(player1, player2, df_match):

    player1_stat = {
                    'Games Won':0,
                    'Tie Break Score':0,
                    'Aces':0,
                    'Double Faults':0,
                    'Total Points Won':0,
                    'Points Win %':0,
                    'Total Points Won Serving':0,
                    'Total Points Won Receiving':0,
                    'Points Won Serving %':0,
                    'Points Won Receiving %':0,
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
                    'Tie Break Score':0,
                    'Aces':0,
                    'Double Faults':0,
                    'Total Points Won':0,
                    'Points Win %':0,
                    'Total Points Won Serving':0,
                    'Total Points Won Receiving':0,
                    'Points Won Serving %':0,
                    'Points Won Receiving %':0,
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


    for _, row in df_match.iterrows():

        server = row['Server']
        receiver = row['Receiver']
        if player1 == server:



            if int(row['Game#']) < 13:
                if int(row['Total Points Won']) > int(row['Total Points Lost']):
                    player1_stat['Games Won'] += 1
                else:
                    player2_stat['Games Won'] += 1
            else:
                player1_stat['Tie Break Score'] += int(row['Total Points Won'])
                player2_stat['Tie Break Score'] += int(row['Total Points Lost'])




            #player1_stat['Points won Serving']  += int(row['Total Points Won'])
            player1_stat['Total Points Won Serving'] += int(row['Total Points Won'])
            player2_stat['Total Points Won Receiving'] += int(row['Total Points Lost'])

            #player1_stat['Total Points Won']  += int(row['Total Points Won'])
            #player2_stat['Total Points Won']  += int(row['Total Points Lost'])
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

            if int(row['Game#']) < 13:
                if int(row['Total Points Won']) > int(row['Total Points Lost']):
                    player2_stat['Games Won'] += 1
                else:
                    player1_stat['Games Won'] += 1
            else:
                player1_stat['Tie Break Score'] += int(row['Total Points Lost'])
                player2_stat['Tie Break Score'] += int(row['Total Points Won'])

            player2_stat['Total Points Won Serving'] += int(row['Total Points Won'])
            player1_stat['Total Points Won Receiving'] += int(row['Total Points Lost'])

            #player2_stat['Total Points Won']  += int(row['Total Points Won'])
            #player1_stat['Total Points Won']  += int(row['Total Points Lost'])
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

    player1_stat['Total Points Won'] = player1_stat['Total Points Won Serving'] + player1_stat['Total Points Won Receiving']
    player2_stat['Total Points Won'] = player2_stat['Total Points Won Serving'] + player2_stat['Total Points Won Receiving']

    temp_value = round(100 * player1_stat['Total Points Won']/ (player1_stat['Total Points Won'] + player2_stat['Total Points Won']),2)
    player1_stat['Points Win %'] = f"{player1_stat['Total Points Won']} ({temp_value}%)"

    temp_value = round(100 * player2_stat['Total Points Won']/ (player1_stat['Total Points Won'] + player2_stat['Total Points Won']),2)
    player2_stat['Points Win %'] = f"{player2_stat['Total Points Won']} ({temp_value}%)"

    temp_value = round(100 * player1_stat['Total Points Won Serving']/ (player1_stat['Total Points Won Serving'] + player2_stat['Total Points Won Receiving']),2)
    player1_stat['Points Won Serving %'] = f"{player1_stat['Total Points Won Serving']} ({temp_value}%)"

    temp_value = round(100 * player2_stat['Total Points Won Serving']/ (player2_stat['Total Points Won Serving'] + player1_stat['Total Points Won Receiving']),2)
    player2_stat['Points Won Serving %'] = f"{player2_stat['Total Points Won Serving']} ({temp_value}%)"

    temp_value = round(100 * player1_stat['Total Points Won Receiving']/ (player1_stat['Total Points Won Receiving'] + player2_stat['Total Points Won Serving']),2)
    player1_stat['Points Won Receiving %'] = f"{player1_stat['Total Points Won Receiving']} ({temp_value}%)"

    temp_value = round(100 * player2_stat['Total Points Won Receiving']/ (player2_stat['Total Points Won Receiving'] + player1_stat['Total Points Won Serving']),2)
    player2_stat['Points Won Receiving %'] = f"{player2_stat['Total Points Won Receiving']} ({temp_value}%)"

    temp_value = round(100*((player1_stat['First Serves'] - player1_stat['First Serve Faults'])/player1_stat['First Serves']),2)
    player1_stat['First Serve %'] = f"{player1_stat['First Serves']} ({temp_value}%)"

    temp_value = round(100*((player2_stat['First Serves'] - player2_stat['First Serve Faults'])/player2_stat['First Serves']),2)
    player2_stat['First Serve %'] = f"{player2_stat['First Serves']} ({temp_value}%)"

    temp_value = round(100*(player1_stat['First Serve Wins']/player1_stat['First Serves']),2)
    player1_stat['First Serve Win %'] = f"{player1_stat['First Serve Wins']} ({temp_value}%)"

    temp_value = round(100*(player2_stat['First Serve Wins']/player2_stat['First Serves']),2)
    player2_stat['First Serve Win %'] = f"{player2_stat['First Serve Wins']} ({temp_value}%)"

    if player1_stat['Second Serves'] != 0:
        temp_value = round(100*((player1_stat['Second Serves'] - player1_stat['Double Faults'])/player1_stat['Second Serves']),2)
        player1_stat['Second Serve %'] = f"{player1_stat['Second Serves']} ({temp_value}%)"

        temp_value = round(100*(player1_stat['Second Serve Wins']/player1_stat['Second Serves']),2)
        player1_stat['Second Serve Win %'] = f"{player1_stat['Second Serve Wins']} ({temp_value}%)"

    else:
        temp_value = "NA"
        player1_stat['Second Serve %'] = f"{player1_stat['Second Serves']} ({temp_value}%)"
        player1_stat['Second Serve Win %'] = f"{player1_stat['Second Serve Wins']} ({temp_value}%)"

    if player2_stat['Second Serves'] != 0:
        temp_value = round(100*((player2_stat['Second Serves'] - player2_stat['Double Faults'])/player2_stat['Second Serves']),2)
        player2_stat['Second Serve %'] = f"{player2_stat['Second Serves']} ({temp_value}%)"

        temp_value = round(100*(player2_stat['Second Serve Wins']/player2_stat['Second Serves']),2)
        player2_stat['Second Serve Win %'] = f"{player2_stat['Second Serve Wins']} ({temp_value}%)"
    else:
        temp_value = "NA"
        player2_stat['Second Serve %'] = f"{player2_stat['Second Serves']} ({temp_value}%)"
        player2_stat['Second Serve Win %'] = f"{player2_stat['Second Serve Wins']} ({temp_value}%)"



    #st.dataframe(df_match)

    stat_rec = []

    display_stats = ['Games Won','Tie Break Score','Points Win %','Points Won Serving %', 'Points Won Receiving %','Aces','Double Faults','First Serve %','First Serve Win %','Second Serve %','Second Serve Win %']

    for stat in player1_stat:

        if stat in display_stats:
            if stat != 'Tie Break Score':
                values = player1_stat[stat],stat,player2_stat[stat]
                stat_rec.append(values)
            else:
                if player1_stat[stat] > 0 or player2_stat[stat] > 0:
                    values = player1_stat[stat],stat,player2_stat[stat]
                    stat_rec.append(values)


    stat_df = pd.DataFrame(stat_rec, columns=[player1,'Match Stats',player2])

    return stat_df





match_results = Load_MatchResults()
df = match_results[match_results['Status'] == 'Completed'].sort_values("Match#")
df.set_index("Match#", inplace=True)


#p_standing = player_standings()

default_image_path = f"{image_dir}/default.jpg"

match_list = [f"{i}-{df.loc[i,'Player1 Name']} vs {df.loc[i,'Player2 Name']}" for i in df.index]

param_id = st.query_params.get("mid")
if param_id:
    match_id = int(param_id)
    match_string = f"{match_id}-{df.loc[match_id,'Player1 Name']} vs {df.loc[match_id,'Player2 Name']}"
    def_match_id = match_list.index(match_string)
else:
    def_match_id = 0


left, right = st.columns((5,6), vertical_alignment="bottom")

match_sel = left.selectbox("Select Match",match_list,def_match_id,label_visibility='collapsed')
left.markdown('<BR>', unsafe_allow_html=True)
match_no = int(match_sel.split("-")[0])
player1 = df.loc[match_no,'Player1 Name']
player2 = df.loc[match_no,'Player2 Name']
winner = df.loc[match_no,'Winner']
match_score = df.loc[match_no,'Match Score']
match_commentary = df.loc[match_no,'Match Commentary']

#params=st.get_params()



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
#right.markdown('<BR>',unsafe_allow_html=True)
#right.write("  ")

right.markdown(html_text,unsafe_allow_html=True)
#right.markdown('<BR>',unsafe_allow_html=True)

show_commentary = right.empty()



show_image = left.empty()

image_path = f"{image_dir}/{match_no}.jpg"

try:
    # Use HTML to control size
    #show_image.image(image_path, use_container_width=True, output_format="PNG")
    show_image.image(image_path, width=600, output_format="PNG")

except:
    show_image.image(default_image_path, width=600, output_format="PNG")


df_stat = Load_MatchStats()



df_match = df_stat[df_stat['Match#'] == match_no]
if len(df_match) < 1:
    st.warning("Stats Not Updated for this Match yet. Be patient")
    st.stop()
else:
    stat_df = get_match_stat(player1, player2, df_match)


commentary_html = f"""
<div style='text-align: center; font-size: 16px;color:magenta'>
{match_commentary}
</div><BR>
"""

show_commentary.markdown(commentary_html,unsafe_allow_html=True)

html_text = get_markdown_stat_table(stat_df)
#st.write(html_text)
right.markdown(html_text, unsafe_allow_html=True)

#st.write(match_results)
