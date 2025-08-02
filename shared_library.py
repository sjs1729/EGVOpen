import pandas as pd
import numpy as np
import random as rm
import streamlit as st
from collections import defaultdict
import pprint
from typing import List, Optional, Tuple, Set
import os
from PIL import Image
import base64
from io import BytesIO

@st.cache_data()
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')


def image_to_base64(img_path):
    img = Image.open(img_path)
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()


def rounded_image_html(image_path, image_size=100):
    img_b64 = image_to_base64(image_path)

    # HTML for rounded image
    html = f"""
    <div style='
        display: flex;
        justify-content: center;
        padding: 10px;
    '>
        <img src='data:image/png;base64,{img_b64}' style='
            width: {image_size}px;
            height: auto;
            border-radius: 20px;
            border: 2px solid #ccc;
            box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
        '/>
    </div>
    """
    return html

class Player:
    def __init__(self, id: int, name: str, age_group: str, tower: str,
                 points: int = 0, rank: int = 0, tb1: int = 0, tb2: int = 0, tb3: int = 0):
        self.id = id
        self.name = name
        self.age_group = age_group
        self.tower = tower
        self.points = points
        self.opponents: set[int] = set()  # Players already faced

    def __repr__(self):
        return f"{self.name}(ID:{self.id},P:{self.points}, Age:{self.age_group}, O:{self.opponents})"


@st.cache_data()
def Load_MatchResults():
    df = pd.read_csv("Match_Results.csv")

    # Convert 'Schedule_Date' to datetime (date only)
    df['Schedule Date'] = pd.to_datetime(df['Schedule Date'], format='%d-%b-%Y')

    # Convert 'Schedule_Time' to datetime.time
    df['Schedule Time'] = pd.to_datetime(df['Schedule Time'], format='%I:%M:%S %p').dt.time

    # Optional: combine date and time into a single datetime column
    df['Scheduled_DateTime'] = df.apply(lambda row: pd.Timestamp.combine(row['Schedule Date'], row['Schedule Time']), axis=1)

    return df

def Load_Players():
    df = pd.read_csv("PlayerList.csv")
    df.set_index('Sr#', inplace=True)



    matches=Load_MatchResults()
    matches = matches[matches['Status'] == 'Completed']
    players = []
    for i in df.index:

        id = i
        name = df.loc[i,'Name']
        age_group = df.loc[i,'Age Group']
        tower = df.loc[i,'Tower']

        #st.write(i,name,seed)
        players.append(Player(id=id,name=name,age_group=age_group, tower=tower))
        #st.write(players)


    if len(matches) > 0 :
        for j in players:
            id = j.id



            matches_id = matches[(matches['Player1#'] == id) | (matches['Player2#'] == id)]

            matches_won = matches_id[matches_id['Winner_Id'] == id]
            j.points = len(matches_won)

            for _, row in matches_id.iterrows():

                if id == row['Player1#']:
                    j.opponents.add(row['Player2#'])
                else:
                    j.opponents.add(row['Player1#'])




    return players

def group_players_by_points(players: List[Player]) -> dict:
    groups = defaultdict(list)
    for p in players:
        groups[p.points].append(p)
    return dict(sorted(groups.items(), reverse=True))


def swiss_pairing(players: List[Player]) -> List[Tuple[Player, Optional[Player]]]:
    #st.write(players)
    pairings = []
    grouped = group_players_by_points(players)
    floaters = []

    for point in list(grouped.keys()):
        group = grouped[point]
        if floaters:
            group = floaters + group
            floaters = []

        group.sort(key=lambda x: x.seed)
        i, j = 0, len(group) - 1
        used = set()

        while i < j:
            p1 = group[i]
            p2 = group[j]

            if p2.id not in p1.opponents:
                pairings.append((p1, p2))
                p1.opponents.add(p2.id)
                p2.opponents.add(p1.id)
                used.add(p1)
                used.add(p2)
                i += 1
                j -= 1
            else:
                # Try next valid pairing by adjusting j
                found = False
                for k in range(j - 1, i, -1):
                    p2_alt = group[k]
                    if p2_alt.id not in p1.opponents and p2_alt not in used:
                        pairings.append((p1, p2_alt))
                        p1.opponents.add(p2_alt.id)
                        p2_alt.opponents.add(p1.id)
                        used.add(p1)
                        used.add(p2_alt)
                        group[k], group[j] = group[j], group[k]  # Maintain loop logic
                        i += 1
                        j -= 1
                        found = True
                        break
                if not found:
                    # No valid opponent found for p1 in current group
                    break

        # Float the unpaired player(s)
        unmatched = [p for p in group if p not in used]
        if unmatched:
            floaters = unmatched + floaters  # Always go on top of next group

    # Handle leftover floater as BYE
    if floaters:
        pairings.append((floaters[0], None))

    return pairings


def get_markdown_col_fields(field_label, field_value, format_amt = 'N'):
    markdown_txt = '<p><span style="font-family: Verdana, Geneva, sans-serif; font-size: 12px;">'
    markdown_txt = markdown_txt + '<span style="color: rgb(20,20,255);"><strong>{}: </strong></span>'.format(field_label)
    if format_amt == 'Y':
        markdown_txt = markdown_txt + '<span style="color: rgb(0,0,0);">{}</span>'.format(display_amount(field_value))
    else:
        markdown_txt = markdown_txt + '<span style="color: rgb(0,0,0);">{}</span>'.format(field_value)

    return markdown_txt

def get_markdown_table(data, header='Y', footer='N'):

    #st.write(data)
    if header == 'Y':

        cols = data.columns
        ncols = len(cols)
        if ncols < 5:
            html_script = "<table><style> table {border-collapse: collapse;width: 100%; border: 1px solid #ddd;}th {background-color: #ffebcc;padding:0px;} td {font-size='5px;text-align:center;padding:0px;'}tr:nth-child(even) {background-color: #fafafa;}</style><thead><tr style='width:100%;border:none;font-family:Courier; color:Red; font-size:14px'>"
        elif ncols < 8:
            html_script = "<table><style> table {border-collapse: collapse;width: 100%; border: 1px solid #ddd;}th {background-color: #ffebcc;padding:0px;} td {font-size='5px;text-align:center;padding:0px;'}tr:nth-child(even) {background-color: #fafafa;}</style><thead><tr style='width:100%;border:none;font-family:Courier; color:Red; font-size:14px'>"
        else:
            html_script = "<table><style> table {border-collapse: collapse;width: 100%; border: 1px solid #ddd;}th {background-color: #ffebcc;padding:0px;} td {font-size='5px;text-align:center;padding:0px;'}tr:nth-child(even) {background-color: #fafafa;}</style><thead><tr style='width:100%;border:none;font-family:Courier; color:Red; font-size:14px'>"


        for i in cols:
            if 'Fund' in i or 'Name' in i:
                html_script = html_script + "<th style='text-align:center'>{}</th>".format(i)
            else:
                html_script = html_script + "<th style='text-align:center''>{}</th>".format(i)

    html_script = html_script + "</tr></thead><tbody>"
    for j in data.index:
        if ncols < 5:
            html_script = html_script + "<tr style='border:none;font-family:Courier;font-weight:600;color:#2C64F6; font-size:14px;padding:1px;';>"
        elif ncols < 8:
            html_script = html_script + "<tr style='border:none;font-family:Courier;font-weight:550;color:#2C64F6; font-size:11px;padding:1px;';>"
        else:
            html_script = html_script + "<tr style='border:none;font-family:Courier;font-weight:550;color:#2C64F6; font-size:12px;padding:1px;';>"

        a = data.loc[j]
        for k in cols:
            if k in ['Round#']:
                html_script = html_script + "<td style='padding:2px;text-align:center' rowspan='1'>{}</td>".format(int(a[k]))
            else:
                html_script = html_script + "<td style='padding:2px;text-align:center' rowspan='1'>{}</td>".format(a[k])

    html_script = html_script + '</tbody></table>'

    return html_script


def player_standings():

    df=Load_MatchResults()
    #df=df[df['Round#'] <= 2]
    players = Load_Players()


    player_stat_rec = []

    #st.write(players)


    for i in range(len(players)):

        tb2 = 0
        tb3 = 0

        id = players[i].id
        opponents = players[i].opponents
        #st.write(id, opponents)


        matches = df[(df['Player1#'] == id) | (df['Player2#'] == id)]


        matches_won = matches[matches['Winner_Id'] == id]
        matches_lost = matches[(matches['Winner_Id'] != id) & (matches['Winner_Id'].notna())]

        n_wins = len(matches_won)
        n_losses = len(matches_lost)



        players[i].points = n_wins

        if n_wins > 0:
            tb2 = get_tb(id, matches_won, players)

        if n_losses > 0:
            tb3 = get_tb(id, matches_lost, players)

        tot_matches = len(matches[matches['Status']=='Completed'])

        i_opp_points = 0
        for j in opponents:
            opponent_id = int(j) - 1
            #st.write(i,players[i], opponent_id, players[opponent_id])
            i_opp_points += players[opponent_id].points



        #st.write(i, i_opp_points)


        values = id, players[i].name,players[i].age_group, tot_matches,n_wins, n_losses,players[i].points, i_opp_points, tb2, tb3, 1000000*players[i].points+ 10000*i_opp_points + 100* tb2 + tb3
        player_stat_rec.append(values)

    player_rank = pd.DataFrame(player_stat_rec, columns=['Player ID','Player Name','AgeGroup','Matches Played','Wins#','Losses#','Points','TB1', 'TB2', 'TB3','RatingPoints'])
    player_rank.set_index('Player ID', inplace=True)
    player_rank['Rank'] = player_rank['RatingPoints'].rank(ascending=False, method='min')
    player_rank['Rank']=player_rank['Rank'].apply(lambda x: int(x))
    return player_rank.sort_values(['RatingPoints','Player Name'], ascending=False)


def get_tb(id,results,players):

    tb2_tot = 0
    for _, row in results.iterrows():
        id_1 = int(row['Player1#'])
        id_2 = int(row['Player2#'])

        if id == id_1:
            tb2_tot = tb2_tot + players[id_2-1].points
        else:
            tb2_tot = tb2_tot + players[id_1-1].points


    return tb2_tot

def get_markdown_player_standings(data):


    cols = data.columns


    ncols = len(cols)

    html_script = "<table><style> table {border-collapse: collapse;width: 100%; border: 1px solid #ddd;}th {background-color: #ffebcc;padding:0px;} td {font-size='5px;text-align:center;padding:0px;'}tr:nth-child(even) {background-color: #f6f6f6;}</style><thead><tr style='width:100%;border:none;font-family:Courier; color:Red; font-size:14px'>"

    #html_script = html_script + "<style>img.player-image {height: 24px; vertical-align: middle; margin-right: 6px;}</style>"

    for i in cols:
        html_script = html_script + "<th style='text-align:center''>{}</th>".format(i)

    html_script = html_script + "</tr></thead><tbody>"

    for j in data.index:

        url_link = "https://egvtennisopen.streamlit.app/Player_Stats?id={}".format(j)

        html_script = html_script + "<tr style='border:none;font-family:Courier; font-weight:550;color:#2C64F6; font-size:12px;padding:1px;';>"
        a = data.loc[j]
        for k in cols:

            if k == 'Player Name':

                html_script += "<td style='padding:2px; text-align:center' rowspan='1'><a href={} style='text-decoration:underline; font-weight:550;color:#2C64F6;'>{}</a></td>".format(url_link,a[k])
            else:
                html_script = html_script + "<td style='padding:2px;text-align:center' rowspan='1'>{}</td>".format(a[k])

    html_script = html_script + '</tbody></table>'

    return html_script




def get_player_id(player_name, players):
    player_id = 0
    for i in players:
        if i.name == player_name:
            return i.id

    return player_id


def get_html_hyperlink_table(data, players, check_status='N'):

    cols = data.columns


    ncols = len(cols)

    html_script = "<table><style> table {border-collapse: collapse;width: 100%; border: 1px solid #ddd;}th {background-color: #ffebcc;padding:0px;} td {font-size='5px;text-align:center;padding:0px;'}tr:nth-child(even) {background-color: #fafafa;}</style><thead><tr style='width:100%;border:none;font-family:Courier; color:Red; font-size:13px'>"

    for i in cols:
        html_script = html_script + "<th style='text-align:center''>{}</th>".format(i)

    html_script = html_script + "</tr></thead><tbody>"

    for j in data.index:


        html_script = html_script + "<tr style='border:none;font-family:Courier; font-weight:550;color:#2C64F6; font-size:13px;padding:1px;';>".format()
        a = data.loc[j]
        for k in cols:

            if k == 'Match#':
                if check_status != 'Y' :
                    match_url_link = "https://egvtennisopen.streamlit.app/Match_Stats?mid={}".format(a[k])
                    html_script += "<td style='padding:2px; text-align:center' rowspan='1'><a href={} style='text-decoration:underline;font-weight:550;color:#2C64F6;'>{}</a></td>".format(match_url_link,a[k])
                else:
                    if a['Status'] == 'Completed':
                        match_url_link = "https://egvtennisopen.streamlit.app/Match_Stats?mid={}".format(a[k])
                        html_script += "<td style='padding:2px; text-align:center' rowspan='1'><a href={} style='text-decoration:underline;font-weight:550;color:#2C64F6;'>{}</a></td>".format(match_url_link,a[k])
                    else:
                        html_script = html_script + "<td style='padding:2px;text-align:center' rowspan='1'>{}</td>".format(a[k])

            elif k in ['Against','Player Name','Player1 Name','Player2 Name']:
                player_id = get_player_id(a[k],players)
                if player_id > 0:
                    player_url_link = "https://egvtennisopen.streamlit.app/Player_Stats?id={}".format(player_id)
                    html_script += "<td style='padding:2px; text-align:center' rowspan='1'><a href={} style='text-decoration:underline;font-weight:550;color:#2C64F6;'>{}</a></td>".format(player_url_link,a[k])
                else:
                    html_script = html_script + "<td style='padding:2px;text-align:center;font-weight:550;color:#2C64F6;' rowspan='1'>{}</td>".format(a[k])
            else:
                html_script = html_script + "<td style='padding:2px;text-align:center;font-weight:550;color:#2C64F6;' rowspan='1'>{}</td>".format(a[k])

    html_script = html_script + '</tbody></table>'

    return html_script
