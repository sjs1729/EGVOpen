import pandas as pd
import numpy as np
import random as rm
import streamlit as st
from shared_library import *
import os


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


def get_tournament_status():
    df = Load_MatchResults()

    nrows = len(df)

    round = 1

    if nrows > 0:
        round = df['Round#'].max()


    return round

logo, heading, buf = st.columns((3,10,3),vertical_alignment="top")
logo.image("EGVOpenLogo.png", width=100)
heading.markdown('<p style="font-size:44px;font-weight: bold;text-align:center;vertical-align:middle;color:#2C64F6;margin:0px;padding:0px">Current Standings</p>', unsafe_allow_html=True)
st.markdown('<BR><BR>', unsafe_allow_html=True)

st.sidebar.markdown("<BR>",unsafe_allow_html=True)
image_html = rounded_image_html("Sponsor.jpg", 300)
st.sidebar.markdown(image_html, unsafe_allow_html=True)
nRound = get_tournament_status()

display_cols=['Rank','Player Name','Matches Played','Wins#','Losses#','Points','TB1', 'TB2', 'TB3']

p_standing = player_standings()
#st.write(p_standing.head())

category_list = ['ALL','Less than 18','18-45','45+']

left, mid, right = st.columns((1.5  ,6,6), vertical_alignment="top")

left.markdown('<p style="font-size:18px;font-weight:550;text-align:left;vertical-align:center;color:Red;margin:px;padding:2px">Age Group</p><BR>', unsafe_allow_html=True)
sel_category = mid.selectbox('Age Group',category_list,0,label_visibility="collapsed")

#p_standing['Rank']=p_standing['Rank'].apply(lambda x: int(x))

if sel_category == 'ALL':
    p_standing['Rank']=p_standing['Rank'].apply(lambda x: int(x))
    html_text1 = get_markdown_player_standings(p_standing[display_cols].sort_values(['Rank','Player Name']))
    st.markdown(html_text1, unsafe_allow_html=True)
else:
    p_standing_cat = p_standing[p_standing['AgeGroup']==sel_category]
    p_standing_cat['Rank'] = p_standing_cat['RatingPoints'].rank(ascending=False, method='min')
    p_standing_cat['Rank'] = p_standing_cat['Rank'].apply(lambda x: int(x))
    html_text1 = get_markdown_player_standings(p_standing_cat[display_cols].sort_values(['Rank','Player Name']))
    st.markdown(html_text1, unsafe_allow_html=True)




#html_text = get_markdown_table(p_standing[display_cols].sort_values(['Rank','Player Name']))



#st.write(html_text)
#st.markdown(html_text, unsafe_allow_html=True)

csvfile = convert_df(p_standing[display_cols])

download_file_name= f"EGV_Tennis_{nRound}_Standings.csv"
st.markdown('<BR>',unsafe_allow_html=True)
st.download_button(
        label="Download CSV",
        data=csvfile,
        file_name=download_file_name,
        mime='text/csv',
        icon=":material/download:",
        key=f"Download_Standings"
)




#player_rank = player_standings()
#html_script = get_markdown_table(player_rank)
#st.markdown(html_script, unsafe_allow_html=True)
