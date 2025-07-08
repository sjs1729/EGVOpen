import pandas as pd
import numpy as np
import random as rm
import streamlit as st
from collections import defaultdict
import pprint
from typing import List, Optional, Tuple, Set
import os


@st.cache_data()
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')

def display_point(player1_score, player2_score):

    score_dict = {0:'0', 1:'15',2:'30',3:'40'}

    if player1_score > 3 and player2_score > 3:

        if abs(player1_score - player2_score) == 2:
            if player1_score > player2_score:
                return 'Game Player 1'
            else:
                return 'Game Player 2'
        elif (player1_score - player2_score) == 0:
            return '40 : 40'
        else:
            if player1_score > player2_score:
                return 'A : 40'
            else:
                return '40 : A'
    elif player1_score == 3 and player2_score == 3:
        return '40 : 40'

    elif player1_score > 3:
        if player2_score < 3:
            return 'Game Player 1'
        else:
            return '40 : 40'

    elif player2_score > 3:
        if player1_score < 3:
            return 'Game Player 2'
        else:
            return '40 : 40'

    else:
        score  = f"{score_dict[player1_score]} : {score_dict[player2_score]}"
        return score


def tennis_game_score(player1_cutoff, display_score='N'):
    player1_score = 0
    player2_score = 0


    while not ((player1_score >= 4 and (player1_score - player2_score) >=2) or (player2_score >= 4 and (player2_score - player1_score) >=2)):
        point_score = rm.randint(1, 100)
        if point_score <= player1_cutoff:
            player1_score += 1
        else:
            player2_score += 1

        if display_score == 'Y':
            print(point_score,display_point(player1_score,player2_score))

    if player1_score > player2_score:
        return 1
    else:
        return 2

def tie_breaker(player1_cutoff, service_corr, first_serve=1):
    player1_score = 0
    player2_score = 0
    points_played = 0

    who_serve = first_serve



    while not ((player1_score >= 7 and (player1_score - player2_score) >=2) or (player2_score >= 7 and (player2_score - player1_score) >=2)):
        point_score = rm.randint(1, 100)

        if who_serve == 1:
            cutoff = player1_cutoff
        else:
            cutoff = player1_cutoff - service_corr

        if point_score <= cutoff:
            player1_score += 1
        else:
            player2_score += 1

        points_played += 1

        if points_played % 2 == 1:
            if who_serve == 1:
                who_serve = 2
            else:
                who_serve = 1

    score = f"{player1_score}-{player2_score}"
    return score, who_serve


def tennis_set_score(player1_advantage, service_corr, who_serves_first=1):

    #toss = rm.randint(1, 2)
    service_counter = who_serves_first
    player1_set_score = 0
    player2_set_score = 0



    while not ((player1_set_score >= 6 or player2_set_score >= 6) and abs(player1_set_score - player2_set_score) >= 2):

        if service_counter == 1:
            cutoff = player1_advantage + service_corr
        else:
            cutoff = player1_advantage - service_corr

        who_won_game = tennis_game_score(cutoff)

        if who_won_game == 1:
            player1_set_score += 1
        else:
            player2_set_score += 1


        set_score = f"{player1_set_score}:{player2_set_score}"
        #print(service_counter, cutoff, set_score)

        if service_counter == 1:
            service_counter = 2
        else:
            service_counter = 1

        if player1_set_score == 6 and player2_set_score == 6:
            tie_breaker_score, who_next = tie_breaker(cutoff, service_corr, first_serve=1)


            tie_breaker_score_1 = int(tie_breaker_score.split("-")[0])
            tie_breaker_score_2 = int(tie_breaker_score.split("-")[1])

            if tie_breaker_score_1 > tie_breaker_score_2:
                return 1, f"7-6({tie_breaker_score_1}-{tie_breaker_score_2})", who_next
            else:
                return 2, f"6-7({tie_breaker_score_1}-{tie_breaker_score_2})", who_next






    if player1_set_score > player2_set_score:
        return 1, f"{player1_set_score}-{player2_set_score}", service_counter
    else:
        return 2, f"{player1_set_score}-{player2_set_score}", service_counter


def tennis_match(player1_seed,player2_seed, service_factor=5, nSets=3):

    who_serves = rm.randint(1, 2)

    match_result = ""

    player1_set_score = 0
    player2_set_score = 0

    seed_diff = min(abs(player1_seed - player2_seed),7)

    base_cutoff = 50

    if player1_seed < player2_seed:
        base_cutoff = base_cutoff + seed_diff
    else:
        base_cutoff = base_cutoff - seed_diff


    while not ( player1_set_score == nSets or player2_set_score == nSets):
        if who_serves == 1:
            cut_off = base_cutoff + service_factor
        else:
            cut_off = base_cutoff - service_factor


        winner, score , who_serves = tennis_set_score(cut_off, service_factor, who_serves)
        match_result = match_result + score + " "
        if winner == 1:
            player1_set_score += 1
        else:
            player2_set_score += 1


    if player1_set_score > player2_set_score:
        return 1, match_result.strip()
    else:
        return 2, match_result.strip()



class Player:
    def __init__(self, id: int, name: str, points: int = 0, seed: int = 0, rank: int = 0, tb1: int = 0, tb2: int = 0, tb3: int = 0):
        self.id = id
        self.name = name
        self.points = points
        self.seed = seed
        self.opponents: Set[int] = set()  # Players already faced

    def __repr__(self):
        return f"{self.name}(P:{self.points}, S:{self.seed}, O:{self.opponents})"



@st.cache_data()
def Load_MatchResults():
    df = pd.read_csv("Match_Results.csv")

    # Convert 'Schedule_Date' to datetime (date only)
    df['Schedule Date'] = pd.to_datetime(df['Schedule Date'], format='%d-%b-%Y')

    # Convert 'Schedule_Time' to datetime.time
    df['Schedule Time'] = pd.to_datetime(df['Schedule Time'], format='%I:%M %p').dt.time

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
        seed = df.loc[i,'Rank']
        name = df.loc[i,'Name']
        players.append(Player(id,name,seed=seed))


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
            html_script = "<table><style> table {border-collapse: collapse;width: 100%; border: 1px solid #ddd;}th {background-color: #ffebcc;padding:0px;} td {font-size='5px;text-align:center;padding:0px;'}tr:nth-child(even) {background-color: #f2f2f2;}</style><thead><tr style='width:100%;border:none;font-family:Courier; color:Red; font-size:14px'>"
        elif ncols < 8:
            html_script = "<table><style> table {border-collapse: collapse;width: 100%; border: 1px solid #ddd;}th {background-color: #ffebcc;padding:0px;} td {font-size='5px;text-align:center;padding:0px;'}tr:nth-child(even) {background-color: #f2f2f2;}</style><thead><tr style='width:100%;border:none;font-family:Courier; color:Red; font-size:14px'>"
        else:
            html_script = "<table><style> table {border-collapse: collapse;width: 100%; border: 1px solid #ddd;}th {background-color: #ffebcc;padding:0px;} td {font-size='5px;text-align:center;padding:0px;'}tr:nth-child(even) {background-color: #f2f2f2;}</style><thead><tr style='width:100%;border:none;font-family:Courier; color:Red; font-size:14px'>"


        for i in cols:
            if 'Fund' in i or 'Name' in i:
                html_script = html_script + "<th style='text-align:center'>{}</th>".format(i)
            else:
                html_script = html_script + "<th style='text-align:center''>{}</th>".format(i)

    html_script = html_script + "</tr></thead><tbody>"
    for j in data.index:
        if ncols < 5:
            html_script = html_script + "<tr style='border:none;font-family:Courier; color:Blue; font-size:12px;padding:1px;';>"
        elif ncols < 8:
            html_script = html_script + "<tr style='border:none;font-family:Courier; color:Blue; font-size:11px;padding:1px;';>"
        else:
            html_script = html_script + "<tr style='border:none;font-family:Courier; color:Blue; font-size:12px;padding:1px;';>"

        a = data.loc[j]
        for k in cols:
            if k in ['Round#']:
                html_script = html_script + "<td style='padding:2px;text-align:center' rowspan='1'>{}</td>".format(int(a[k]))
            else:
                html_script = html_script + "<td style='padding:2px;text-align:center' rowspan='1'>{}</td>".format(a[k])

    html_script = html_script + '</tbody></table>'

    return html_script


def player_standings(round):

    df=Load_MatchResults()
    df=df[df['Round#'] <= 2]
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
        #st.write(matches)

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


        values = id, players[i].name, tot_matches,n_wins, n_losses,players[i].points, i_opp_points, tb2, tb3, 1000000*players[i].points+ 10000*i_opp_points + 100* tb2 + tb3
        player_stat_rec.append(values)

    player_rank = pd.DataFrame(player_stat_rec, columns=['Player ID','Player Name','Matches Played','Wins#','Loses#','Points','TB1', 'TB2', 'TB3','RatingPoints'])
    player_rank.set_index('Player ID', inplace=True)
    player_rank['Rank'] = player_rank['RatingPoints'].rank(ascending=False, method='min')
    player_rank['Rank']=player_rank['Rank'].apply(lambda x: int(x))
    return player_rank.sort_values(['Points','TB1', 'TB2', 'TB3','Player Name'], ascending=False)


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

def get_markdown_player_standings(data, image_column):

    image_dir = "./images"
    def_image = "default.webp"


    cols = data.columns
    ncols = len(cols)
    if ncols < 5:
        html_script = "<table><style> table {border-collapse: collapse;width: 100%; border: 1px solid #ddd;}th {background-color: #ffebcc;padding:0px;} td {font-size='5px;text-align:center;padding:0px;'}tr:nth-child(even) {background-color: #f2f2f2;}</style><thead><tr style='width:100%;border:none;font-family:Courier; color:Red; font-size:14px'>"
    elif ncols < 7:
        html_script = "<table><style> table {border-collapse: collapse;width: 100%; border: 1px solid #ddd;}th {background-color: #ffebcc;padding:0px;} td {font-size='5px;text-align:center;padding:0px;'}tr:nth-child(even) {background-color: #f2f2f2;}</style><thead><tr style='width:100%;border:none;font-family:Courier; color:Red; font-size:12px'>"
    else:
        html_script = "<table><style> table {border-collapse: collapse;width: 100%; border: 1px solid #ddd;}th {background-color: #ffebcc;padding:0px;} td {font-size='8px;text-align:center;padding:0px;'}tr:nth-child(even) {background-color: #f2f2f2;}</style><thead><tr style='width:100%;border:none;font-family:Courier; color:Red; font-size:10px'>"

    html_script = html_script + "<style>img.player-image {height: 24px; vertical-align: middle; margin-right: 6px;}</style>"

    for i in cols:
        if 'Fund' in i or 'Name' in i:
            html_script = html_script + "<th style='text-align:left'>{}</th>".format(i)
        else:
            html_script = html_script + "<th style='text-align:center''>{}</th>".format(i)

    html_script = html_script + "</tr></thead><tbody>"
    for j in data.index:
        if ncols < 5:
            html_script = html_script + "<tr style='border:none;font-family:Courier; color:Blue; font-size:12px;padding:1px;';>"
        elif ncols < 7:
            html_script = html_script + "<tr style='border:none;font-family:Courier; color:Blue; font-size:11px;padding:1px;';>"
        else:
            html_script = html_script + "<tr style='border:none;font-family:Courier; color:Blue; font-size:14px;padding:1px;';>"

        a = data.loc[j]
        for k in cols:
            if image_column in k :
                last_name = a[k].split()[-1]
                image_file_name = f"{last_name}.webp"
                image_path = os.path.join(image_dir, image_file_name)

                if not os.path.exists(image_path):
                    image_path = os.path.join(image_dir, def_image)


                html_script = html_script + '<td><img src="{}" class="player-image">{}</td>'.format(image_path,a[k])
            else:
                html_script = html_script + "<td style='padding:2px;text-align:center' rowspan='1'>{}</td>".format(a[k])

    html_script = html_script + '</tbody></table>'

    return html_script
