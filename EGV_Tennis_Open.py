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





st.markdown('<p style="font-size:40px;font-weight: bold;text-align:center;vertical-align:middle;color:blue;margin:0px;padding:0px">EGV Tennis Open</p>', unsafe_allow_html=True)

@st.cache_data()
def Load_Players():
    df = pd.read_csv("player_seedings.csv")
    players = []
    for i in df.index:
        id = i
        seed = df.loc[i,'Rank']
        name = df.loc[i,'Name']
        players.append(Player(id,name,seed=seed))

    return players

match_res_cols = ['Match#','Round#','Id1','Player1','Id2','Player2','Match_Result','Winner']

def how_many_rounds(nplayers):
    return int(np.ceil(np.log(nplayers)/np.log(2)))

if 'match_number' not in st.session_state:
    st.session_state.match_number = 0

if 'player_list' not in st.session_state:
    st.session_state.player_list = Load_Players()

if 'tournament_status' not in st.session_state:
    st.session_state.tournament_status = {'pairing_status' : 0,
                                          'match_completion' : 0
                                         }

if 'match_results' not in st.session_state:
    st.session_state.match_results = pd.DataFrame(columns=match_res_cols)


def get_tournament_status():
    df = st.session_state.match_results
    nrows = len(df)

    round = 1

    if nrows > 0:
        round = df['Round#'].max() + 1


    return round



nPlayers = len(st.session_state.player_list)
tot_rounds = how_many_rounds(nPlayers)

st.markdown('<BR><BR>',unsafe_allow_html=True)
st.markdown(get_markdown_col_fields("No of Players",nPlayers),unsafe_allow_html=True)
st.markdown(get_markdown_col_fields("Total Rounds to be Played",tot_rounds),unsafe_allow_html=True)
st.markdown(get_markdown_col_fields("Total Rounds to be Played",how_many_rounds(nPlayers)),unsafe_allow_html=True)
st.markdown('<BR>', unsafe_allow_html=True)

nRound = get_tournament_status()

display_cols=['Rank','Player Name','Matches Played','Wins#','Loses#','Points','TB1', 'TB2', 'TB3']

if nRound <= tot_rounds:

    if st.button(f"Start Round {nRound}"):
        pairings = swiss_pairing(st.session_state.player_list)
        m_rec = []
        for i in pairings:
            st.session_state.match_number += 1
            p1 = i[0]
            player1_seed = p1.id
            player1_name = p1.name


            if i[1] is not None:

                p2 = i[1]
                player2_seed = p2.id
                player2_name = p2.name

                winner, match_score = tennis_match(player1_seed,player2_seed, service_factor=5, nSets=3)
                winner_id = i[winner - 1].id
                i[winner-1].points = i[winner-1].points + 1
                values = st.session_state.match_number, nRound, player1_seed,player1_name, player2_seed, player2_name, match_score, winner_id

            else:
                winner_id = player1_seed
                match_score = 'Bye'
                values = st.session_state.match_number, nRound, player1_seed,player1_name, "", "", match_score, winner_id
                i[0].points = i[0].points + 1

            m_rec.append(values)

        df_round = pd.DataFrame(m_rec, columns=match_res_cols)

        st.session_state.match_results = pd.concat([st.session_state.match_results,df_round], axis=0)

        player_rank = player_standings()
        html_script = get_markdown_table(player_rank[display_cols])

        if nRound > tot_rounds:
            st.success(f"{tot_rounds} Rounds Completed. Final Rankings")
        else:
            st.success(f"Standings after Round {nRound}")


        st.markdown(html_script, unsafe_allow_html=True)


else:
    if st.button(f"Start Again"):
        st.session_state.clear()
        st.rerun()
    st.success(f"{tot_rounds} Rounds Completed. Final Rankings")
    player_rank = player_standings()
    html_script = get_markdown_table(player_rank[display_cols])
    st.markdown(html_script, unsafe_allow_html=True)
