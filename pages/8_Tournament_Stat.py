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
    df['Deuces'] = df.apply(
        lambda x: (x['Total Points Won'] + x['Total Points Lost'] - 6) / 2
        if (x['Total Points Won'] + x['Total Points Lost']) > 6 else 0,
        axis=1
    )
    df['Service Breaks'] = df.apply(
        lambda x: 1  if x['Total Points Won'] < x['Total Points Lost'] else 0,
        axis=1
    )

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



def get_html_table_scroll(data, header='Y'):
    if header == 'Y':

        cols = data.columns
        ncols = len(cols)



        html_script = "<style> .tableFixHead {overflow-y: auto; height: 400px;}"
        html_script = html_script + ".tableFixHead thead th {position: sticky; top: 0px;}"
        html_script = html_script + "table {border-collapse: collapse; width: 100%;}"
        html_script = html_script + "th, td {padding: 8px 16px; border: 1px solid #cc} th {background: #eee;}"
        html_script = html_script + "tr:nth-child(even) {background-color: #f2f2f2;}</style>"
        html_script = html_script + '<div class="tableFixHead"><table><thead>'
        html_script = html_script + "<tr style='border:none;font-family:Courier; color:Red; font-size:12px;'>"

        for i in cols:
            if i in ['SCHEMES','SCHEME_CATEGORY','FUND_HOUSE']:
                html_script = html_script + "<th style='text-align:left;background-color: #ffebcc;'>{}</th>".format(i)
            else:
                html_script = html_script + "<th style='text-align:center;background-color: #ffebcc;'>{}</th>".format(i)

    html_script = html_script + "</tr></thead><tbody>"
    for j in data.index:
        #url_link = "http://localhost:8501/Fact_Sheet?id={}".format(j)
        url_link = "https://growealth.streamlit.app/Fact_Sheet?id={}".format(j)


        html_script = html_script + "<tr style='border:none;font-family:Courier; color:Blue; font-size:10px;'>"
        a = data.loc[j]
        for k in cols:
            if k in ['Rel_MaxDD','Prob_10Pct','NIFTY_CORR']:
                html_script = html_script + "<td style='padding:2px;text-align:center' rowspan='1'>{}</td>".format(round(a[k],2))
            elif k in ['SCHEME_CATEGORY','FUND_HOUSE']:
                html_script = html_script + "<td style='padding:2px;text-align:left' rowspan='1'>{}</td>".format(a[k])
            elif k == 'SCHEMES':
                #html_script = html_script + "<td style='padding:2px;text-align:left' rowspan='1'><a href={}>{}</a></td>".format(url_link,a[k])
                html_script = html_script + "<td style='padding:2px;text-align:left' rowspan='1'><a href={}>{}</a></td>".format(url_link,a[k])
                #st.write(url_link,a[k])
            else:
                html_script = html_script + "<td style='padding:2px;text-align:center' rowspan='1'>{}</td>".format(a[k])




    html_script = html_script + '</tbody></table>'

    return html_script

def get_markdown_dict(dict, font_size = 10, format_amt = 'N'):


    html_script = """
                <table><style> table {border-collapse: collapse;width: 100%; border: 1px solid #ddd;}th {background-color: #ffebcc;padding:0px;}
                 td {font-size='5px;text-align:center;padding:0px;'}tr:nth-child(even) {background-color: #f2f2f2;}</style><thead>
                 <tr style='width:100%;border:none;font-family:Courier; color:Red; font-size:15px'>
                 """


    for j in dict.keys():

        if dict[j] == dict[j]:
            html_script = html_script + "<tr style='border:none;font-family:Courier; color:#2C64F6; font-size:{}px;padding:1px;';>".format(font_size)
            html_script = html_script + "<td style='border:none;padding:2px;font-family:Courier; color:#2C64F6; font-size:{}px;text-align:left' rowspan='1'>{}</td>".format(font_size,j)
            if format_amt == 'N':
                html_script = html_script + "<td style='border:none;padding:4px;font-family:Courier; color:#EC6B30; font-size:{}px;text-align:left' rowspan='1'>{}</td>".format(font_size -1,dict[j])
            else:
                html_script = html_script + "<td style='border:none;padding:4px;font-family:Courier; color:#EC6B30; font-size:{}px;text-align:right' rowspan='1'>{}</td>".format(font_size -1,display_amount(dict[j]))



    html_script = html_script + '</tbody></table>'

    return html_script



image_dir = "images"


logo, heading, buf = st.columns((3,10,3),vertical_alignment="top")
logo.image("EGVOpenLogo.png", width=100)
heading.markdown('<p style="font-size:44px;font-weight: bold;text-align:center;vertical-align:middle;color:blue;margin:0px;padding:0px">Tournament in Numbers</p>', unsafe_allow_html=True)
st.markdown('<BR><BR>', unsafe_allow_html=True)


players = Load_Players()
p_standing = player_standings()





df = Load_MatchResults()
df=df[df['Status'] == 'Completed']

df_stat = Load_MatchStats()


#st.write(df_stat)



t_stats = {
            'Total Matches': len(df_stat['Match#'].unique()),
            'Total Games': df_stat[df_stat['Game#']< 13]['Game#'].count(),
            'Total Tie Breaks': df_stat[df_stat['Game#'] == 13]['Game#'].count(),
            'Total Deuces': int(df_stat['Deuces'].sum()),
            'Total Points': int(df_stat['Total Points Won'].sum() + df_stat['Total Points Lost'].sum()),
            'Total First Serves': int(df_stat['First Serves'].sum()),
            'Total Faults': df_stat['Second Serves'].sum(),
            'First Serve %': f"{round(100 * int(df_stat['First Serves'].sum() - df_stat['Second Serves'].sum())/int(df_stat['First Serves'].sum()),2)}%",
            'Total Second Serves': int(df_stat['Second Serves'].sum()),
            'Total Double Faults': int(df_stat['Double Faults'].sum()),
            'Double Faults %': f"{round(100 * int(df_stat['Double Faults'].sum())/int(df_stat['Second Serves'].sum()),2)}%",
            'Total Aces': int(df_stat['Aces'].sum()),
            'Total Service Breaks': int(df_stat[df_stat['Service Breaks']==1]['Service Breaks'].count())
}


html_text = get_markdown_dict(t_stats,16)

left, center, right = st.columns((5,2,5))
left.markdown('<p style="font-size:24px;font-weight: bold;text-align:center;vertical-align:middle;color:blue;margin:0px;padding:0px">Overall Tournament Stats</p>', unsafe_allow_html=True)
left.markdown(html_text, unsafe_allow_html=True)

p_standing = player_standings()

#st.write(p_standing)

pl_stats = []
pl_columns = ['Player ID','Player Name','Aces','Double Faults','Games Won','Games Lost','Points Won','Points Won Serving','Points Won Receiving','Service Breaks','Service Break - Conceded']
for idx, row in p_standing.iterrows():
    if idx < 45:
        p_name=row['Player Name']


        n_aces = df_stat[df_stat['Server']==p_name]['Aces'].sum()
        n_dbl_flt = df_stat[df_stat['Server']==p_name]['Double Faults'].sum()
        n_points_won_serving = df_stat[df_stat['Server']==p_name]['Total Points Won'].sum()
        n_points_lost_serving = df_stat[df_stat['Server']==p_name]['Total Points Lost'].sum()
        games_won_serving = df_stat[(df_stat['Server']==p_name) & (df_stat['Service Breaks'] == 0) & (df_stat['Game#'] < 13)]['Service Breaks'].count()
        games_lost_receiving = df_stat[(df_stat['Receiver']==p_name) & (df_stat['Service Breaks'] == 0) & (df_stat['Game#'] < 13)]['Service Breaks'].count()

        n_points_won_receiving = df_stat[df_stat['Receiver']==p_name]['Total Points Lost'].sum()
        n_points_lost_receiving = df_stat[df_stat['Receiver']==p_name]['Total Points Won'].sum()

        n_points_won = n_points_won_serving + n_points_won_receiving
        n_points_lost = n_points_lost_serving + n_points_lost_receiving

        n_service_breaks_conceded = df_stat[(df_stat['Server']==p_name) & (df_stat['Service Breaks'] == 1) & (df_stat['Game#'] < 13)]['Service Breaks'].sum()
        n_services_broken = df_stat[(df_stat['Receiver']==p_name) & (df_stat['Service Breaks'] == 1) & (df_stat['Game#'] < 13)]['Service Breaks'].sum()

        n_games_won = games_won_serving + n_services_broken
        n_games_lost = games_lost_receiving + n_service_breaks_conceded
        values = idx, p_name, n_aces,n_dbl_flt, n_games_won, n_games_lost,n_points_won, n_points_won_serving,n_points_won_receiving,n_services_broken,n_service_breaks_conceded

        pl_stats.append(values)

pl_stats_df = pd.DataFrame(pl_stats, columns=pl_columns)

#st.write(pl_stats_df)

#left, buf, right = st.columns([6,1,6])

select_options = ['Aces','Double Faults','Games Won','Games Lost','Points Won','Points Won Serving','Points Won Receiving','Service Breaks','Service Break - Conceded']

right.markdown('<p style="font-size:18px;font-weight: bold;text-align:center;vertical-align:middle;color:blue;margin:0px;padding:0px">Top 10 -  Stats</p>', unsafe_allow_html=True)

sel_category = right.selectbox('Stats - Top 10',select_options,0, label_visibility='collapsed')

#p_standing['Rank']=p_standing['Rank'].apply(lambda x: int(x))

disp_cols = ['Rank','Player Name',sel_category]

if sel_category in ['Double Faults','Games Lost','Service Break - Conceded']:
    pl_stats_df['Rank'] = pl_stats_df[sel_category].rank(ascending=True, method='min')
    pl_stats_df['Rank'] = pl_stats_df['Rank'].apply(lambda x: int(x))
    html_text1 = get_html_table_scroll(pl_stats_df[disp_cols].sort_values(['Rank','Player Name']))
    #html_text1 = get_markdown_table(pl_stats_df[disp_cols].sort_values(['Rank','Player Name']).head(10))

    right.markdown(html_text1, unsafe_allow_html=True)
else:
    pl_stats_df['Rank'] = pl_stats_df[sel_category].rank(ascending=False, method='min')
    pl_stats_df['Rank'] = pl_stats_df['Rank'].apply(lambda x: int(x))
    html_text1 = get_html_table_scroll(pl_stats_df[disp_cols].sort_values(['Rank','Player Name']))
    #html_text1 = get_markdown_table(pl_stats_df[disp_cols].sort_values(['Rank','Player Name']).head(10))

    right.markdown(html_text1, unsafe_allow_html=True)

csvfile = convert_df(pl_stats_df[disp_cols].sort_values(['Rank','Player Name']))

download_file_name= f"EGV_Tennis_{sel_category}_Standings.csv"
right.markdown('<BR>',unsafe_allow_html=True)
right.download_button(
        label="Download Full List",
        data=csvfile,
        file_name=download_file_name,
        mime='text/csv',
        icon=":material/download:",
        key=f"Download_Standings"
)
