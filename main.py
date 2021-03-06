from flask import Flask, Blueprint, flash, g, redirect, render_template, request, session, url_for
import werkzeug
#from flask_session.__init__ import Session

## GETTING DATE AND TIME
from datetime import date
from dateutil.relativedelta import relativedelta
today = date.today()
this_year = date.today().strftime('%Y')
current_year = '2021'

from time import sleep

import cpl_main
import numpy as np
import os
import pandas as pd
import re

canpl = Flask(__name__)
# Set the secret key to some random bytes. Keep this really secret!
canpl.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# get all player information and store it in one dataframe
# create a new column to allow better filtering by year
player_info_19 = pd.read_csv(f'datasets/2019/league/2019-player-info.csv')
player_info_19['year'] = '2019'
player_info_20 = pd.read_csv(f'datasets/2020/league/2020-player-info.csv')
player_info_20['year'] = '2020'
player_info_21 = pd.read_csv(f'datasets/2021/league/2021-player-info.csv')
player_info_21['year'] = '2021'
player_info = pd.concat([ player_info_19, player_info_20, player_info_21 ])

# get all player names and store these in one dataframe
# create a dictionary for better retrieval of the names
player_names_df = pd.concat([ player_info_19[['name','display']] , player_info_20[['name','display']], player_info_21[['name','display']] ])
player_names_df = player_names_df.sort_values(by='name')
player_names_df = player_names_df.drop_duplicates()
player_names = {}
for c,r in player_names_df.iterrows():
    player_names[r['name']] = r['display']
    player_names[r['display']] = r['display']

ccd_names = {'Atlético Ottawa' : 'Atlético Ottawa',
            'Cavalry' : 'Cavalry FC',
            'Edmonton' : 'FC Edmonton',
            'Forge' : 'Forge FC',
            'HFX Wanderers' : 'HFX Wanderers FC',
            'Pacific' : 'Pacific FC',
            'Valour' : 'Valour FC',
            'York United' : 'York United FC',
            'York United' : 'York9 FC','York9' : 'York9 FC'}

team_names = {'Atlético Ottawa' : 'ato',
              'Cavalry FC' : 'cav','Cavalry' : 'cav',
              'FC Edmonton' : 'fce','Edmonton' : 'fce',
              'Forge FC' : 'for','Forge' : 'for',
              'HFX Wanderers FC' : 'hfx','HFX Wanderers' : 'hfx',
              'Pacific FC' : 'pac','Pacific' : 'pac',
              'Valour FC' : 'val','Valour' : 'val',
              'York United FC' : 'yor','York United' : 'yor',
              'York9 FC' : 'y9','York9' : 'y9'}

team_colour = {'Atlético Ottawa' : '#fff',
              'Cavalry FC' : '#fff',
              'FC Edmonton' : '#fff',
              'Forge FC' : '#fff',
              'HFX Wanderers FC' : '#052049',
              'Pacific FC' : '#fff',
              'Valour FC' : '#fff',
              'York United FC' : '#003b5c',
              'York9 FC' : '#003b5c'}

col_check = {'overall':'O',
            'Aerials':'air',
            'BgChncFace':'BgChF',
            'ChncOpnPl':'Ch-c',
            'CleanSheet':'CS',
            'Clrnce':'Clr',
            'DefTouch':'defTch',
            'Disposs':'dis',
            'DuelLs':'DlL',
            'DuelsW%':'DlW',
            'ExpA':'xA',
            'ExpG':'xG',
            'ExpGAg':'xGc',
            'FlComA3':'FlA3',
            'FlSufM3':'Flsuf',
            'Goal':'G',
            'GoalCnIBx':'GcBox',
            'GoalCncd':'Gc',
            'Int':'int',
            'Off':'shtTrg',
            'Pass%':'Pc%',
            'PsAtt':'Pat',
            'PsCmpA3':'Pata',
            'PsCmpM3':'Patm',
            'PsOnHfFl':'Pfd',
            'PsOpHfFl':'Pfa',
            'PsOpHfScs':'Psuca',
            'Recovery':'Rec',
            'Saves':'SV',
            'SucflDuels':'sDl',
            'SucflTkls':'sTkl',
            'SvClct':'SVc',
            'SvDive':'dvS',
            'SvHands':'hdS',
            'SvInBox':'SVi',
            'SvOutBox':'SVo',
            'SvPrdSaf':'SVps',
            'SvStand':'SVstn',
            'TchsA3':'Tcha',
            'TchsM3':'Tchm',
            'TouchOpBox':'TchoB',
            'Touches':'Tch'}

tooltip = {'O':'Overall Score',
            'air':'Aerials Duels Won',
            'BgChF':'Big Chances Faced',
            'Ch-c':'Chances Created from Open Play',
            'CS':'Clean Sheets',
            'Clr':'Clearances',
            'defTch':'Defensive Touches',
            'dis':'Dispossed',
            'DlL':'Duels Lost',
            'DlW':'Successful Duels',
            'xA':'Expected Assists',
            'xG':'Expected Goals',
            'xGc':'Expected Goals Conceded',
            'FlA3':'Fouls Committed in the Attacking Third',
            'Flsuf':'Fouls Suffered in the Middle Third',
            'G':'Goals',
            'GcBox':'Goals Condeded from Inside the Box',
            'Gc':'Goals Conceded',
            'int':'Interceptions',
            'shtTrg':'Shots Off Target',
            'Pc%':'Pass Completion Percentage',
            'Pat':'Passes Attempted',
            'Pata':'Passes Completed from the Attacking Third',
            'Patm':'Passes Completed from the Middle Third',
            'Pfd':'Failed Passed in Own Half',
            'Pfa':'Failed Passes in Opponents Half',
            'Psuca':'Successful Passes in Opponents Half',
            'Rec':'Recoveries',
            'SV':'Saves',
            'sDl':'Successful Duels',
            'sTkl':'Successful Tackles',
            'SVc':'Saves Collected',
            'dvS':'Diving Saves',
            'hdS':'Saves with the Hands',
            'SVi':'Saves from shots Inside the Box',
            'SVo':'Saves from shots Outside the Boix',
            'SVps':'Saves Parried into Safety',
            'SVstn':'Saves while Standing',
            'Tcha':'Touches in the Attacking Third',
            'Tchm':'Touches in the Middle Third',
            'TchoB':'Touches in the Opponents Box',
            'Tch':'Touches',
            'Min':'Minutes Played',}

contributors = {
    'tam':'Todd McCullough',
    'bot':'Match Bot',
    'lab':'The Cook Book',
}

geegle = ['#000000','#ffffff','#ffd700','#ff00ff','#4a86e8','#0000ff','#9900ff','#ff00ff']

def new_col(data):#,chart=''
    for col in data.columns:
        try:
            data[col_check[col]] = data[col]
            if col_check[col]:
                data.pop(col)
        except:
            pass
    for col in data.columns:
        try:
            if col in ['display','number']:
                temp = data.pop(col)
                data[col] = temp
        except:
            pass
    return data

def convert_num_str(num):
    num = str(num*100)
    return num[0:4]

def get_year():
    '''try:
        session['year'] = request.form['year']
        return session.get('year'), ''
    except KeyError as error:
        session['year'] = '2020'
        return session.get('year'), error # if "year" hasn't been set yet, return None'''
    error = None
    if request.method == 'POST':
        try:
            print('REQUESTING YEAR: ')
            print(request.form['year'])
            return request.form['year'], error
        except Exception as error:
            print(error)
            return '2021' , error
    else:
        return '2021' , error

def load_main_files(year):

    results = pd.read_csv(f'datasets/{year}/league/{year}-results.csv')

    try:
        week = results[results['hr'] == 'E']['w'].head(1).values[0]
        schedule = results[results['w'] == week].copy()
        schedule = schedule.fillna(0)
    except:
        week = results['w'].tail(1).values[0]
        schedule = results[results['w'] == week].copy()

    stats = pd.read_csv(f'datasets/{year}/playerstats/{year}-stats.csv')
    stats_seed = pd.read_csv(f'datasets/{year}/playerstats/{year}-stats-seed.csv')

    team_ref = pd.read_csv('datasets/teams.csv')
    team_ref = team_ref[team_ref['year'] == int(year)]
    player_info = pd.read_csv(f'datasets/{year}/league/{year}-player-info.csv')

    results_old = results[results['hr'] != 'E'].copy()
    results_diff = pd.concat([results, results_old]).drop_duplicates()

    if results_diff.empty:
        results_diff = results_old.tail(1)

    colours = team_ref['colour']

    results_brief = cpl_main.get_results_brief(results,year)

    return results, team_ref, player_info, results_old, results_diff, schedule, results_brief

def check_dataframe(data,file,column,year):
    ## check to see if there is stats available for the season
    if data.at[0,column] == 'tbd':
        last_year = str(int(year)-1)
        data = pd.read_csv(f'datasets/{last_year}/playerstats/{last_year}-{file}.csv')
    if data.at[0,column] == 'tbd':
        data
    return data

def load_player_files(year,check=1):

    # get all rated player information based on position and calculate and overall score for the individual player
    rated_assists = pd.read_csv(f'datasets/{year}/playerstats/{year}-assists.csv')
    rated_assists = check_dataframe(rated_assists,'assists','name',year)
    rated_goalscorers = pd.read_csv(f'datasets/{year}/playerstats/{year}-goalscorers.csv')
    rated_goalscorers = check_dataframe(rated_goalscorers,'goalscorers','name',year)
    rated_offenders = pd.read_csv(f'datasets/{year}/playerstats/{year}-discipline.csv')

    stats = {'goals' : rated_goalscorers['Goal'].sum(),'assists' : rated_assists['Ast'].sum(),'yellow' : rated_offenders['Yellow'].sum(),'red' : rated_offenders['Red'].sum()}

    if check == 0:
        return stats

    rated_forwards = pd.read_csv(f'datasets/{year}/playerstats/{year}-forwards.csv')
    rated_forwards = check_dataframe(rated_forwards,'forwards','name',year)
    rated_midfielders = pd.read_csv(f'datasets/{year}/playerstats/{year}-midfielders.csv')
    rated_midfielders = check_dataframe(rated_midfielders,'midfielders','name',year)
    rated_defenders = pd.read_csv(f'datasets/{year}/playerstats/{year}-defenders.csv')
    rated_defenders = check_dataframe(rated_defenders,'defenders','name',year)
    rated_keepers = pd.read_csv(f'datasets/{year}/playerstats/{year}-keepers.csv')
    rated_keepers = check_dataframe(rated_keepers,'keepers','name',year)

    return rated_forwards, rated_midfielders, rated_defenders, rated_keepers, rated_offenders, rated_goalscorers, rated_assists, stats

# get current day and set time variables
month, day, weekday = cpl_main.get_weekday()
games_played = {1:28,2:7}
# set the year - which will change based on user choice
year = '2021'
error = ''

@canpl.context_processor
def inject_user():

    return dict(today = today, day = day, weekday = weekday, month = month, theme = 'mono', current_year = current_year, error = error)

@canpl.route('/setsession')
def setsession():
    session['Username'] = 'Admin'
    return f"The session has been Set"

@canpl.route('/getsession')
def getsession():
    if 'Username' in session:
        Username = session['Username']
        return f"Welcome {Username}"
    else:
        return "Welcome Anonymous"

@canpl.route('/popsession')
def popsession():
    session.pop('Username',None)
    return "Session Deleted"

@canpl.route('/', methods=['GET','POST'])
def index():

    na = 'TBD'
    session['year'] = '2021'
    year, error = get_year()

    results, team_ref, player_info, results_old, results_diff, schedule, results_brief = load_main_files(year)
    stats = load_player_files(year,check=0)

    championship = pd.read_csv(f'datasets/{year}/league/{year}-championship.csv')
    playoffs = pd.read_csv(f'datasets/{year}/league/{year}-playoffs.csv')
    standings = pd.read_csv(f'datasets/{year}/league/{year}-regular-standings.csv')
    standings_old = pd.read_csv(f'datasets/{year}/league/{year}-regular-standings-prev.csv')
    rankings = pd.read_csv(f'datasets/{year}/league/{year}-power_rankings.csv')
    rankings = rankings.sort_values(by='rank')

    if championship.at[0,'team'] == 'TBD':
        top_team = standings.iloc[0]['team']
        top_team_info = team_ref[team_ref['team'].str.contains(top_team)]
        first_colour = top_team_info.iloc[0]['colour']
        first_crest = top_team_info.iloc[0]['crest']
        top_mover = rankings.iloc[0]['team']
        top_crest = team_ref[team_ref['team'].str.contains(top_mover)]
        top_crest = top_crest.iloc[0]['crest']
        top_dropper = rankings.iloc[-1]['team']
        bot_crest = team_ref[team_ref['team'].str.contains(top_dropper)]
        bot_crest = bot_crest.iloc[0]['crest']
        if standings.at[0,'matches'] == 0:
            headline = f'{year} Season Starts June 26th'
        else:
            headline = f'{year} Season'

    else:
        top_team = championship.iloc[0]['team']
        top_team_info = team_ref[team_ref['team'].str.contains(top_team)]
        first_colour = top_team_info.iloc[0]['colour']
        first_crest = top_team_info.iloc[0]['crest']
        top_mover = standings.iloc[0]['team']
        top_crest = team_ref[team_ref['team'].str.contains(top_mover)]
        top_crest = top_crest.iloc[0]['crest']

        if year == '2019':
            top_dropper = playoffs.iloc[-1]['team']
        else:
            top_dropper = standings.iloc[-1]['team']

        bot_crest = team_ref[team_ref['team'].str.contains(top_dropper)]
        bot_crest = bot_crest.iloc[0]['crest']
        if championship.at[0,'matches'] == 0:
            headline = f'{year} Playoffs'
        else:
            headline = f'{year} Season Completed'

    #game_week, goals, big_win, top_team, low_team, other_team, assists, yellows, reds
    game_week, goals, big_win, top_result, low_result, other_result, assists, yellows, reds = cpl_main.get_weeks_results(year,results,standings,stats,team_ref,team_names)

    # set the headlines to dynamically change based on what year is being viewed
    if year != '2021':
        timeframe = 1
        results_headline = 'Top Results of the Season'
        players_headline = 'Top Players of the Season'
    else:
        if standings.iloc[0]['matches'] == 0:
            timeframe = 0
            results_headline = 'Season Yet to Start'
            players_headline = f'Top Players of {int(year)-1}'
        else:
            timeframe = 1
            results_headline = 'Top Results of the Week'
            players_headline = 'Top Players of the Week'

    top_scorer =  player_info[player_info['gl'] == 1 ][['name','overall']].copy().reset_index(drop=True)
    top_assist =  player_info[player_info['al'] == 1 ][['name','overall']].copy().reset_index(drop=True)
    top_forward = player_info[player_info['p'] == 4 ][['name','overall']].copy().reset_index(drop=True)
    top_midfielder = player_info[player_info['p'] == 3 ][['name','overall']].copy().reset_index(drop=True)
    top_defender = player_info[player_info['p'] == 2 ][['name','overall']].copy().reset_index(drop=True)
    top_keeper = player_info[player_info['p'] == 1 ][['name','overall']].copy().reset_index(drop=True)
    top_offender = player_info[player_info['ol'] == 1 ][['name','overall']].copy().reset_index(drop=True)

    if results.iloc[0]['hr'] == 'E':
        top_team, top_mover, top_dropper, first_crest, top_crest, bot_crest, first_colour = na, na, na, 'CPL-Crest-White.png', 'oneSoccer_nav.png', 'canNat_icon.png', 'w3-indigo'

    suspended = ['none']

    return render_template('index.html', year = year, top_mover = top_mover, top_dropper = top_dropper,
    goals = goals,  assists = assists, yellows = yellows, reds = reds,
    big_win = big_win, top_result = top_result, low_result = low_result, other_result = other_result,
    top_team = top_team, top_keeper = top_keeper,top_forward = top_forward,
    top_midfielder = top_midfielder, top_defender = top_defender,
    top_scorer = top_scorer, top_assist = top_assist, top_offender = top_offender, suspended = suspended,
    first_crest = first_crest, first_colour = first_colour, top_crest = top_crest, bot_crest = bot_crest,
    headline = headline, timeframe = timeframe,results_headline = results_headline, players_headline = players_headline)

@canpl.route('/todate', methods=['GET','POST'])
def todate():

    season_tables = {}
    for yr in range(2019,int(year)+1):
        try:
            season_tables[yr] = pd.read_csv(f'datasets/{yr}/league/{yr}-season_totals.csv')
        except:
            pass

    team_ref = pd.read_csv(f'datasets/teams.csv')

    def get_crest(data,yr):
        data['crest'] = '-'
        team_check = team_ref[team_ref['year'] == yr]
        for c,r in data.iterrows():
            data.at[c,'crest'] = team_check[team_check['team'] == r['team']]['crest'].values[0]
        return data

    yeartodate_season_total = pd.DataFrame()
    for k in season_tables.keys():
        yeartodate_season_total = pd.concat([season_tables[k],yeartodate_season_total])
        season_tables[k] = season_tables[k].sort_values(by=['points','gd','win'],ascending = False)
        season_tables[k] = season_tables[k].reset_index(drop=True)
        season_tables[k] = get_crest(season_tables[k],k)

    yeartodate_season_total = yeartodate_season_total.groupby('team').sum()
    yeartodate_season_total = yeartodate_season_total.reset_index()
    yeartodate_season_total = yeartodate_season_total.sort_values(by=['points','gd','win'],ascending = False)
    yeartodate_season_total = yeartodate_season_total.reset_index(drop=True)
    # clean out old team names
    for c,r in yeartodate_season_total.iterrows():
        if r['team'] == 'York9 FC':
            yeartodate_season_total.at[c,'team'] = 'York United FC'
    yeartodate_season_total = get_crest(yeartodate_season_total,int(year))

    columns = yeartodate_season_total.columns

    return render_template('todate.html',columns = columns,
    yeartodate_table = yeartodate_season_total, season_tables = season_tables,
    year = this_year,
    headline = 'Year to Date')

@canpl.route('/standings', methods=['GET','POST'])
def standings():

    year, error = get_year()

    standings = pd.read_csv(f'datasets/{year}/league/{year}-regular-standings.csv')
    headline = 'Top 10 Goals / Assists for '
    if standings.at[0,'matches'] == 0:
        check = 1
        last_year = str(int(year)-1)
        standings = pd.read_csv(f'datasets/{last_year}/league/{last_year}-regular-standings.csv')
        championship = pd.read_csv(f'datasets/{last_year}/league/{last_year}-championship.csv')
        playoffs = pd.read_csv(f'datasets/{last_year}/league/{last_year}-playoffs.csv')
        headline = 'Previous Season Standings for '
        year = last_year
    else:
        championship = pd.read_csv(f'datasets/{year}/league/{year}-championship.csv')
        playoffs = pd.read_csv(f'datasets/{year}/league/{year}-playoffs.csv')
        headline = 'Standings'


    championship = championship.sort_values(by=['points','gd','win'],ascending = False)
    championship = championship.reset_index(drop=True)

    playoffs = playoffs.sort_values(by=['points','gd','win'],ascending = False)
    playoffs = playoffs.reset_index(drop=True)

    standings = standings.sort_values(by=['points','gd','win'],ascending = False)
    standings = standings.reset_index(drop=True)

    team_form_results = pd.read_csv(f'datasets/{year}/league/{year}-team_form.csv')
    team_ref = pd.read_csv(f'datasets/teams.csv')
    team_ref = team_ref[team_ref['year'] == int(year)]

    def get_crest(data,column):
        data['crest'] = '-'
        for i in range(data.shape[0]):
            data.at[i,'crest'] = team_ref[team_ref['team'] == data.at[i,column]]['crest'].values[0]
        return data

    if championship.at[0,'team'] == 'TBD':
        print(f'\n{standings}\n')
        standings = get_crest(standings,'team')
        team_form_results = get_crest(team_form_results,'index')

        columns = standings.columns

        return render_template('standings.html',columns = columns,
        standings_table = standings,
        form_table = team_form_results, year = year,
        headline = 'Standings')
    else:
        championship = get_crest(championship,'team')
        playoffs = get_crest(playoffs,'team')
        standings = get_crest(standings,'team')
        team_form_results = get_crest(team_form_results,'index')

        columns = standings.columns

        return render_template('standings.html',columns = columns,
        championship_table = championship, standings_table = standings, playoffs_table = playoffs,
        form_table = team_form_results, year = year,
        headline = headline)

@canpl.route('/eleven', methods=['GET','POST'])
def eleven():

    year, error = get_year()

    best_eleven_t = pd.DataFrame()
    for pos in ['keepers','defenders','forwards','midfielders']:
        best_eleven_t = pd.concat([pd.read_csv(f'datasets/{year}/playerstats/{year}-{pos}.csv'),best_eleven_t])
    best_eleven_t = best_eleven_t.reset_index(drop=True)
    player_info = pd.read_csv(f'datasets/{year}/league/{year}-player-info.csv')
    headline = 'Best Eleven'

    if best_eleven_t.at[0,'name'] == 'tbd':
        headline = f'Previous Season Best Eleven of '
        best_eleven_t = pd.DataFrame()
        last_year = str(int(year)-1)
        player_info = pd.read_csv(f'datasets/{last_year}/league/{last_year}-player-info.csv')
        for pos in ['keepers','defenders','forwards','midfielders']:
            best_eleven_t = pd.concat([pd.read_csv(f'datasets/{last_year}/playerstats/{last_year}-{pos}.csv'),best_eleven_t])

    best_eleven_t = best_eleven_t.sort_values(by=['overall'],ascending=False)
    best_eleven_t = best_eleven_t.reset_index(drop=True)

    best_eleven_t['tp'] = 0
    for c,r in best_eleven_t.iterrows():
        try:
            best_eleven_t.at[c,'tp'] = player_info[player_info['name'] == r['name']]['tp'].values[0]
        except:
            try:
                best_eleven_t.at[c,'tp'] = player_info[player_info['display'] == r['name']]['tp'].values[0]
            except:
                try:
                    best_eleven_t.at[c,'tp'] = player_info[player_info['name'].str.contains(r['name'].split(' ')[-1])]['tp'].values[0]
                except:
                    try:
                        best_eleven_t.at[c,'tp'] = player_info[player_info['display'].str.contains(r['name'].split(' ')[-1])]['tp'].values[0]
                    except:
                        print(f"{r['name']} missing info")

    best_eleven = pd.DataFrame()
    pos_dict= {
        1:'Keeper',2:'Right Back',3:'Left Back',4:'Rt Center Back',
        5:'Lt Center Back',6:'Defensive Mid',7:'Right Winger',
        8:'Box-to-Box Mid',9:'Striker',10:'Playmaker',11:'Left Winger',
    }
    num_list = [4,1,5,2,6,8,3,7,10,9,11]
    team_colour = {'Atlético Ottawa' : 'cpl-ato',
                  'Cavalry FC' : 'cpl-cfc',
                  'FC Edmonton' : 'cpl-fce',
                  'Forge FC' : 'cpl-ffc',
                  'HFX Wanderers FC' : 'cpl-hfx',
                  'Pacific FC' : 'cpl-pfc',
                  'Valour FC' : 'cpl-vfc',
                  'York United FC' : 'cpl-yor',
                  'York9 FC' : 'cpl-y9'}

    for i in num_list:
        try:
            name = best_eleven_t[best_eleven_t['tp'] == i].head(1)['name'].values[0]
        except:
            name = best_eleven_t[best_eleven_t['tp'] == 4].head(2)['name'].values[1]
        db = player_info[player_info['name'] == name][['team','image','name','display','number','flag','overall','position','link','tp']].copy().reset_index(drop=True)
        db['colour'] = team_colour[db['team'].values[0]]
        db['pos#'] = pos_dict[i]
        best_eleven = pd.concat([db,best_eleven])

    return render_template('eleven.html',
    html_table = best_eleven,  headline = headline, year = year)

@canpl.route('/power', methods=['GET','POST'])
def power():

    year, error = get_year()
    print(year)
    team_ref = pd.read_csv('datasets/teams.csv')
    power = pd.read_csv(f'datasets/{year}/league/{year}-power_rankings.csv')
    standings = pd.read_csv(f'datasets/{year}/league/{year}-regular-standings.csv')

    if power['move'].max() == 0 and standings.at[0,'matches'] == 0:
        print("BROKEN",standings.at[0,'matches'])
        year = str(int(year)-1)
        team_ref = team_ref[team_ref['year'] == int(year)]
        headline = f'Previous Season Power Rankings of '
        power = pd.read_csv(f'datasets/{year}/league/{year}-power_rankings.csv')
    else:
        if year != this_year:
            headline = f'Final Power Rankings for '
        else:
            headline = 'Power Rankings '
        team_ref = team_ref[team_ref['year'] == int(year)]

    for i in range(power.shape[0]):
        power.at[i,'crest'] = team_ref[team_ref['team'] == power.at[i,'team']]['crest'].values[0]
        power.at[i,'colour'] = team_ref[team_ref['team'] == power.at[i,'team']]['colour'].values[0]

    return render_template('power.html', year = year, html_table = power, headline = headline)

@canpl.route('/versus', methods=['GET','POST'])
def versus():

    year = current_year

    matches_predictions = pd.read_csv(f'datasets/{year}/league/{year}-match_predictions.csv')
    if matches_predictions.empty:
        year = str(int(year)-1)
        matches_predictions = pd.read_csv(f'datasets/{year}/cpl-{year}-match_predictions.csv')
        game_form = pd.read_csv(f'datasets/{year}/league/{year}-game_form.csv')
    else:
        game_form = pd.read_csv(f'datasets/{year}/league/{year}-game_form.csv')

    results, team_ref, player_info, results_old, results_diff, schedule, results_brief = load_main_files(year)
    player_info = pd.read_csv(f'datasets/{year}/league/{year}-player-info.csv')
    schedule = pd.read_csv(f'datasets/{year}/league/{year}-results.csv')
    schedule = schedule[schedule['hr']=='E']

    results_old, stats_old = pd.DataFrame(), pd.DataFrame()
    for yr in range(2019,int(year)+1):
        prev_results = pd.read_csv(f'datasets/{year}/league/{year}-results.csv')
        prev_stats = pd.read_csv(f'datasets/{year}/playerstats/{year}-stats.csv')
        results_old = pd.concat([prev_results,results_old])
        stats_old = pd.concat([prev_stats,stats_old])

    team_colours_dict = {}

    print(matches_predictions)

    team_names = {
    'Atlético Ottawa' : 'ato',
    'Cavalry FC' : 'cav',
    'FC Edmonton' : 'fce',
    'Forge FC' : 'for',
    'HFX Wanderers FC' : 'hfx',
    'Pacific FC' : 'pac',
    'Valour FC' : 'val',
    'York United FC' : 'yor',
                  }

    try:
        request_team_name = request.form['home'][:3]
        for long_name,short_name in team_names.items():
            if short_name == request_team_name:
                q1 = long_name
        print(f'retrieved {q1}')
    except:
        q1 = matches_predictions.iloc[0]['home']
        print(f'default {q1}')

    # home side
    home_team_info = team_ref[team_ref['team'] == q1]
    home_colour = home_team_info.iloc[0]['colour']
    home_fill = home_team_info.iloc[0]['colour2']
    home_text = team_colour[q1]
    home_crest = home_team_info.iloc[0]['crest']

    game_info = schedule[schedule['home'] == q1]
    game = game_info.iloc[0]['game']

    # away side
    q2 = game_info.iloc[0]['away']
    away_team_info = team_ref[team_ref['team'] == q2]
    away_colour = away_team_info.iloc[0]['colour']
    away_fill = away_team_info.iloc[0]['colour2']
    away_text = team_colour[q2]
    away_crest = away_team_info.iloc[0]['crest']

    home_win = matches_predictions[(matches_predictions['home'] == q1) & (matches_predictions['away'] == q2)]['home_p'].values[0]
    draw = matches_predictions[(matches_predictions['home'] == q1) & (matches_predictions['away'] == q2)]['draw_p'].values[0]
    away_win = matches_predictions[(matches_predictions['home'] == q1) & (matches_predictions['away'] == q2)]['away_p'].values[0]
    home_form = game_form[q1]
    away_form = game_form[q2]

    home_roster = cpl_main.best_roster(q1, player_info)
    away_roster = cpl_main.best_roster(q2, player_info)

    home_score = matches_predictions[(matches_predictions['home'] == q1) & (matches_predictions['away'] == q2)]['hs'].values[0]
    away_score = matches_predictions[(matches_predictions['home'] == q1) & (matches_predictions['away'] == q2)]['as'].values[0]

    # get previous results
    results_19 = pd.read_csv(f'datasets/2019/league/2019-results.csv')
    results_20 = pd.read_csv(f'datasets/2020/league/2020-results.csv')

    if results.empty:
        results_todate = pd.concat([results_19,results_20])
    else:
        results_todate = pd.concat([results_19,results_20,results])

    results_todate['home'] = results_todate['home'].apply(lambda x: 'York United FC' if x == 'York9 FC' else x)
    results_todate['away'] = results_todate['away'].apply(lambda x: 'York United FC' if x == 'York9 FC' else x)

    compare = cpl_main.get_team_comparison(results_todate,q1,q2)
    q1_r = cpl_main.get_match_history(compare,q1)
    q2_r = cpl_main.get_match_history(compare,q2)

    print(q1_r,q2_r)


    team1, team2, team3, team4, team5, team6, team7, team8 = cpl_main.get_team_files(schedule,team_ref)
    print(team1, team2, team3, team4, team5, team6, team7, team8)

    if (home_win < draw) and (away_win < draw):
        home_win, away_win = draw, draw

    home_win = round(round(home_win,3)*100,3)
    away_win = round(round(away_win,3)*100,3)
    draw = round(round(draw,3)*100,3)

    group1 = team1 + '-' + team2
    if team3 == 1:
        group2 = 1
        group3 = 1
        group4 = 1
    else:
        group2 = team3 + '-' + team4
        if team5 == 1:
            group3 = 1
            group4 = 1
        else:
            group3 = team5 + '-' + team6
            group4 = team7 + '-' + team8

    radar = pd.read_csv(f'datasets/{year}/league/{year}-radar.csv')
    homet = max(q1.split(' '), key=len)
    awayt = max(q2.split(' '), key=len)
    home_radar = radar[radar['team'].str.contains(homet)]
    home_radar = home_radar.reset_index(drop=True)
    away_radar = radar[radar['team'].str.contains(awayt)]
    away_radar = away_radar.reset_index(drop=True)

    home_sum = home_roster['overall'].sum()
    away_sum = away_roster['overall'].sum()

    # get the week that the matches will be played and display the value
    try:
        week = results[results['hr'] == 'E']['w'].head(1).values[0]
    except:
        week = results['w'].tail(1).values[0]

    if results.iloc[-2]['hr'] != 'E':
        headline = f'{year} Finals: {q1} vs {q2}'
    else:
        headline = f'{year} Season: Week {week} Matches:'

    return render_template('versus.html',
    home_team = q1, home_table = home_roster.head(11), home_win = home_win, home_history = q1_r,
    home_crest = home_crest, home_colour = home_colour, home_fill = home_fill, home_radar = home_radar, home_text = home_text,
    away_team = q2, away_table = away_roster.head(11), away_win = away_win, away_history = q2_r,
    away_crest = away_crest, away_colour = away_colour, away_fill = away_fill, away_radar = away_radar, away_text = away_text,
    draw = draw, home_form = home_form, away_form = away_form,
    headline = headline, year = year,
    home_score = home_score, away_score = away_score,
    team1 = team1, team2 = team2, team3 = team3, team4 = team4, team5 = team5, team6 = team6, team7 = team7, team8 = team8,
    group1 = group1, group2 = group2, group3 = group3, group4 = group4)

@canpl.route('/teams', methods=['GET','POST'])
def teams():

    year, error = get_year()

    team_ref = pd.read_csv('datasets/teams.csv')
    team_ref = team_ref[team_ref['year'] == int(year)]
    columns = team_ref.columns

    return render_template('teams.html', year = year, columns = columns, headline = 'Club Information',
    html_table = team_ref, roster = roster)

@canpl.route('/charts', methods=['GET','POST'])
def charts():

    year, error = get_year()

    team_standings = pd.read_csv(f'datasets/{year}/league/{year}-regular-standings.csv')
    if team_standings.at[0,'matches'] == 0:
        team_standings = pd.read_csv(f'datasets/{int(year)-1}/league/{int(year)-1}-regular-standings.csv')
    radar = pd.read_csv(f'datasets/{year}/league/{year}-radar.csv')
    team_standings = team_standings.sort_values(by='team')
    team_standings['xg'] = round((team_standings['Goal'] / team_standings['matches'])*7,2)
    team_standings['xp'] = round(team_standings['points'] / team_standings['matches'],2)
    print(team_standings)
    team_standings['xt'] = team_standings['xp'] * 7
    team_standings['xg'] = team_standings['xg'].astype('int')
    team_standings['xt'] = team_standings['xt'].astype('int')
    team_standings = team_standings.reset_index(drop=True)

    team_ref = pd.read_csv('datasets/teams.csv')
    team_ref = team_ref[team_ref['year'] == int(year)]

    team_list = sorted([x for x in team_ref['team'].unique()])

    ### GET TEAM LINE CHARTS
    team_dict = {}
    team_stats = {}
    for team in team_ref['team'].unique():
        team_stats[team] = []
        team_dict[team] = pd.read_csv(f'datasets/{year}/league/{year}-{team}-line.csv')
        team_stats[team].append(team_dict[team].loc[team_dict[team].shape[0]-1]['ExpG'])
        team_stats[team].append(team_dict[team].loc[team_dict[team].shape[0]-1]['ExpA'])
        team_stats[team].append(round( team_dict[team]['Goal'].sum() / team_dict[team].shape[0],2))
        team_dict[team] = team_dict[team][team_dict[team].columns[2:]].T
        team_dict[team] = cpl_main.index_reset(team_dict[team]).values.tolist()

    columns = team_ref.columns

    stat_cols = ['ExpG','ExpA','Goal','BgChnc','Chance','CleanSheet','GoalCncd','BgChncFace']

    return render_template('charts.html',columns = columns, html_table = team_ref, stat_cols = stat_cols[2:],
    team_list = team_list, team_dict = team_dict, team_stats = team_stats, year = year, geegle = geegle,
    stats = team_standings, radar = radar, headline = 'Radar & Line Charts')

@canpl.route('/roster', methods=['GET','POST'])
def roster():

    year, error = get_year()
    try:
        team = request.form['team']
    except:
        team = session['team']
        if year != '2021' and team == 'York United FC':
            team = 'York9 FC'
        if team == 'York9 FC' and year == '2021':
            team = 'York United FC'

    radar = pd.read_csv(f'datasets/{year}/league/{year}-radar.csv')
    radar = radar[radar['team'] == team]
    radar = cpl_main.index_reset(radar)

    player_info = pd.read_csv(f'datasets/{year}/league/{year}-player-info.csv')
    roster = player_info[player_info['team'] == team][['name','image','position','number','flag','overall','link']]
    team_ref = pd.read_csv('datasets/teams.csv')
    team_ref = team_ref[team_ref['year'] == int(year)]
    coach = team_ref[team_ref['team'] == team][['cw','cl','cd','coach','country','image','w','l','d','year']]

    roster_team_info = team_ref[team_ref['team'] == team].copy()
    roster_team_info = roster_team_info.reset_index(drop=True)
    roster_colour = roster_team_info.iloc[0]['colour']
    crest = roster_team_info.iloc[0]['crest']
    colour1 = roster_team_info.iloc[0]['colour1']
    colour2 = roster_team_info.iloc[0]['colour2']

    team_stats = []
    team_line = pd.read_csv(f'datasets/{year}/league/{year}-{team}-line.csv')
    team_stats.append(team_line.loc[team_line.shape[0]-1]['ExpG'])
    team_stats.append(team_line.loc[team_line.shape[0]-1]['ExpA'])
    team_stats.append(round( team_line['Goal'].sum() / team_line.shape[0],2))
    team_line = team_line[team_line.columns[2:]].T
    team_line = cpl_main.index_reset(team_line).values.tolist()

    session['team'] = team

    return render_template('roster.html', year = year, team_name = team, coach = coach, radar = radar, team_line = team_line, team_stats = team_stats,
    crest = crest, colour1 = colour1, colour2 = colour2, html_table = roster, team_colour = roster_colour, headline = 'Roster Info')

@canpl.route('/team-compare', methods=['GET','POST'])
def teamcompare():

    headline = f'Team Comparison'

    variable_list = ['team1','team1YR','team2','team2YR']
    default_values = {}
    for x in variable_list:
        try:
            default_values[x] = session[x]
        except:
            session[x] = ''
            default_values[x] = session[x]
            print(default_values[x])

    ## request ALL values in request.form create BLANKS if not received
    ###############################################################
    stat_values = {}
    refresh_check = 0
    for x in variable_list:
        try:
            stat_values[x] = request.form[x]
            refresh_check+=1
        except:
            refresh_check=0
            print(x,' exception')
            stat_values[x] = ''

    # Get the selected year for the first choice
    if stat_values['team1YR']:
        pass
    else:
        if refresh_check == 0:
            stat_values['team1YR'] = '2021'
            session['team1YR'] = stat_values['team1YR']
        elif default_values['team1YR']:
            stat_values['team1YR'] = default_values['team1YR']
        else:
            stat_values['team1YR'] = '2021'

    # Get the selected year for the team 2 choice
    if stat_values['team2YR']:
        if refresh_check == 0:
            stat_values['team2YR'] = '2021'
            session['team2YR'] = stat_values['team2YR']
        else:
            pass
    else:
        if refresh_check == 0:
            stat_values['team2YR'] = '2021'
            session['team2YR'] = stat_values['team2YR']
        elif default_values['team1YR']:
            stat_values['team2YR'] = default_values['team2YR']
        else:
            stat_values['team2YR'] = '2021'

    year1 = stat_values['team1YR']
    year2 = stat_values['team2YR']

    # ENSURE that if ATO is selected, 2019 is not selected
    year_correct = {'Atlético Ottawa':'2020','York United FC':'2021'}
    if (default_values['team1'] == 'Atlético Ottawa') & (year1 == '2019'):
        year1 = year_correct['Atlético Ottawa']

    if (default_values['team2'] == 'Atlético Ottawa') & (year2 == '2019'):
        year2 = year_correct['Atlético Ottawa']

    if (default_values['team1'] == 'York United FC') & (year1 in ['2019','2020']):
        stat_values['team1'] = 'York9 FC'

    if (default_values['team2'] == 'York United FC') & (year2 in ['2019','2020']):
        stat_values['team2'] = 'York9 FC'

    if (default_values['team1'] == 'York9 FC') & (int(year1) > 2020):
        stat_values['team1'] = 'York United FC'

    if (default_values['team2'] == 'York9 FC') & (int(year2) > 2020):
        stat_values['team2'] = 'York United FC'

    standings = pd.read_csv(f'datasets/{current_year}/league/{current_year}-regular-standings.csv')
    team_ref = pd.read_csv('datasets/teams.csv')
    team_ref1 = team_ref[team_ref['year'] == int(year1)].copy()
    team_ref1 = team_ref1.reset_index(drop=True)
    team_ref2 = team_ref[team_ref['year'] == int(year2)].copy()
    team_ref2 = team_ref2.reset_index(drop=True)

    team1_select_list = team_ref1.team.unique().tolist()
    team2_select_list = team_ref2.team.unique().tolist()

    if year1 == '2020':
        try:
            team1_select_list.remove('York United FC')
        except:
            pass
    if year2 == '2020':
        try:
            team2_select_list.remove('York United FC')
        except:
            pass
    if year1 == '2019':
        try:
            team1_select_list.remove('Atlético Ottawa')
        except:
            pass
    if year2 == '2019':
        try:
            team2_select_list.remove('Atlético Ottawa')
        except:
            pass

    # Get the selected team for the first choice
    duplicate = 0
    if stat_values['team1']:
        if refresh_check == 0:
            stat_values['team1'] = standings.at[0,'team']
            session['team1'] = stat_values['team1']
        else:
            pass
    else:
        if refresh_check == 0:
            stat_values['team1'] = standings.at[0,'team']
            session['team1'] = stat_values['team1']
        elif (default_values['team1'] != '') & (stat_values['team1YR'] != ''):
            stat_values['team1'] = default_values['team1']
        elif default_values['team1'] == stat_values['team2']:
            duplicate = 1
            stat_values['team1'] == stat_values['team2']
        elif (default_values['team1'] != '') & (stat_values['team2'] != ''):
            stat_values['team1'] == default_values['team1']
        else:
            stat_values['team1'] = team_ref1.at[0,'team']

    # Get the selected team for the team 2 choice
    if stat_values['team2']:
        if duplicate:
            stat_values['team2'] = stat_values['team1']
        if refresh_check == 0:
            stat_values['team2'] = team_ref1.at[1,'team']
            session['team2'] = stat_values['team2']
    else:
        if refresh_check == 0:
            stat_values['team2'] = standings.at[1,'team']
            session['team2'] = stat_values['team2']
        elif (default_values['team2'] != '') & (stat_values['team2YR'] != ''):
            stat_values['team2'] = default_values['team2']
        elif default_values['team1'] == stat_values['team1']:
            stat_values['team2'] == stat_values['team1']
        elif (default_values['team2'] != '') & (stat_values['team1'] != ''):
            stat_values['team2'] == default_values['team2']
        else:
            stat_values['team2'] = team_ref1.at[1,'team']

    team1 = stat_values['team1']
    team2 = stat_values['team2']

    def get_team_details(data,team):
        crest = data[data['team'] == team]['crest'].values[0]
        colour = data[data['team'] == team]['colour'].values[0]
        colour1 = data[data['team'] == team]['colour1'].values[0]
        cw = data[data['team'] == team]['cw'].values[0]
        cd = data[data['team'] == team]['cd'].values[0]
        cl = data[data['team'] == team]['cl'].values[0]
        coach = data[data['team'] == team]['coach'].values[0]
        return crest,colour,colour1,cw,cd,cl,coach

    team1_information = {}
    team1_information['crest'],team1_information['colour'],team1_information['colour2'],team1_information['cw'],team1_information['cd'],team1_information['cl'],team1_information['coach'] = get_team_details(team_ref1,team1)

    team1_line = pd.read_csv(f'datasets/{year1}/league/{year1}-{team1}-line.csv')

    team2_information = {}
    team2_information['crest'],team2_information['colour'],team2_information['colour2'],team2_information['cw'],team2_information['cd'],team2_information['cl'],team2_information['coach'] = get_team_details(team_ref2,team2)

    team2_line = pd.read_csv(f'datasets/{year2}/league/{year2}-{team2}-line.csv')

    def compare_two(q1,db,q2,df,column='ExpG'):

        if q1==q2:
            q1='t1'
            q2='t2'

        def get_norm(data):
            df = data.copy()
            cols = [x for x in data.columns if x not in ['Goal','GoalCncd']]
            for col in cols:
                df[col] = round(df[col]/ df[col].max() ,2)
                df[col] = df[col].fillna(0)
            return df

        # compare the shapes of the dataframes - require similar length
        # take the shortest one
        compare = pd.DataFrame()
        if db.shape[0] > df.shape[0]:
            c = df.shape[0]
        else:
            c = db.shape[0]

        db = get_norm(db)
        df = get_norm(df)

        compare[q1] = db[column].head(c).tolist() # played one more game that season
        compare[q2] = df[column].head(c).tolist()

        return compare
    ############## END OF compare_two lines function

    results = {}
    for x in ['Goal','GoalCncd','CleanSheet','BgChnc','Chance']:
        results[x] = compare_two(team1,team1_line,team2,team2_line,column=x)

    team_lines, line_columns = [], []
    for x in results:
        line_columns.append(x)
        team_lines.append(results[x].T.values.tolist())

    colour1, colour2 = team1_information['colour2'],team2_information['colour2']

    if (colour1 == '#3b7324') & (colour2 == '#78BE20'):
        colour1 = '#DA291C'
    if (colour2 == '#78BE20') & (colour2 == '#3b7324'):
        colour2 = '#DA291C'
    if (colour1 == '#102f52') & (colour2 == '#004C97'):
        colour1 = '#E4002B'
    if (colour2 == '#004C97') & (colour2 == '#102f52'):
        colour2 = '#E4002B'

    def change_hex(col, amt):
        vals = tuple(int(col.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        g,b,r = vals[0]+amt, vals[1]+amt, vals[2]+int(amt/2)
        new_col = '#%02x%02x%02x' % (g,r,b)
        return str(new_col)

    if colour1 == colour2:
        colour2 = change_hex(colour2,60)
        if len(colour2) > 7:
            colour2 = colour2[:7]

    session['team1'] = team1
    session['team1YR'] = year1
    session['team2'] = team2
    session['team2YR'] = year2

    colour1 = '#caf0f8'#'#fff1d0'
    colour2 = '#001219'#'#003b5c'

    for x in range(len(team_lines)):
        t = ['Goal','GoalCncd','CleanSheet','BgChnc','Chance']
        print(t[x])
        print(team_lines[x])

    return render_template('team-compare.html', geegle = geegle, headline= headline,
    team1_select_list = team1_select_list,team2_select_list = team2_select_list,
    team1_colour = team1_information['colour'],team1_crest = team1_information['crest'], team1_cw = team1_information['cw'],
    team1_cd = team1_information['cd'],team1_cl = team1_information['cl'], team1_coach = team1_information['coach'],
    team2_colour = team2_information['colour'],team2_crest = team2_information['crest'], team2_cw = team2_information['cw'],
    team2_cd = team2_information['cd'],team2_cl = team2_information['cl'], team2_coach = team2_information['coach'],
    year1 = year1, year2 = year2,
    team_names = [team1,team2], chart_team_colour_list = [colour1, colour2],
    team_line = team_lines[0],line_columns = line_columns,team_line_2 = team_lines[1],
    team_line_3 = team_lines[2],team_line_4 = team_lines[3],team_line_5 = team_lines[4],
    colour1 = colour1, colour2 = colour2, colour3 = geegle[2])

@canpl.route('/compare', methods=['GET','POST'])
def compare():

    headline = f'Player Comparison'

    variable_list = ['player1_pos','player1','player1YR','player2_pos','player2','player2YR']
    default_values = {}
    for x in variable_list:
        try:
            if x in ['player1','player2']:
                default_values[x] = player_names[session[x]]
            else:
                default_values[x] = session[x]
        except:
            session[x] = ''
            default_values[x] = session[x]


    ## request ALL values in request.form create BLANKS if not received
    ###############################################################
    stat_values = {}
    for x in variable_list:
        try:
            stat_values[x] = request.form[x]
            session[x] = request.form[x]
            refresh_check=1
        except:
            refresh_check=0
            stat_values[x] = ''

    get_name = {'defenders':2,'forwards':10,'keepers':0,'midfielders':5}

    current_year = 2021
    begun = {'no':0,'yes':1}
    year = '2021'
    best_eleven = pd.read_csv(f'datasets/{year}/playerstats/{year}-best_eleven.csv')
    if best_eleven.at[0,'name'] == 'tbd':
        previous_year = int(year)-1
        best_eleven = pd.read_csv(f'datasets/{previous_year}/playerstats/{previous_year}-best_eleven.csv')

    ## GET player list for Position
    ###############################################################
    stat_lists = {}
    stat_lines = {}
    player_info = {}
    for pos in ['defenders','forwards','keepers','midfielders']:
        for yr in range(2019,current_year+1):
            stat_lists[pos[:1]+'_'+str(yr)[2:]] = pd.read_csv(f'datasets/{yr}/playerstats/{yr}-{pos}.csv')
            stat_lines[pos[:1]+'_'+str(yr)[2:]+'_l'] = pd.read_csv(f'datasets/{yr}/playerstats/{yr}-{pos}-line.csv')
            player_info[str(yr)[2:]] = pd.read_csv(f'datasets/{yr}/league/{yr}-player-info.csv')
            player_info[str(yr)[2:]]['year'] = str(yr)

    ### get user selection and apply it to existing data
    ##################################

    def confirm_position(name,position,year):
        # function to comfirm if player played in a selected year
        # if not, then select the most recent year
        get_pos = {'d':'defenders','f':'forwards','g':'keepers','m':'midfielders'}
        def confirm_year(name):
            def check(yr):
                for col in ['name','display']:
                    try:
                        return player_info[yr][player_info[yr][col] == name]['position'].values[0]
                    except:
                        return player_info[yr][player_info[yr][col].str.contains(name.split(' ')[-1])]['position'].values[0]

            y = ['2019','2020','2021']
            year_list = {}
            while y:
                x = y.pop(-1)
                print(f"\nSearching {x}\n")
                try:
                    p = check(x[2:])
                    year_list[x] = [x,get_pos[p]]
                except:
                    print(f"{name} not found")
                    pass
            return year_list

        year_list = confirm_year(name)
        years = [x for x in year_list.keys()]
        if year in years:
            return year_list[year][1], year_list[year][0]
        else:
            try:
                return year_list[years[0]][1], year_list[years[0]][0]
            except:
                print(f"Trouble confirming {name}'s active years")
                return year_list[years[0]][1], year_list[years[0]][0]

    def check_choice(name,position,year,n='1'):
        ## nested functions
        def get_best_eleven(position,n=0):
            return best_eleven.at[get_name[position]+n,'name']

        def loop_data(name,position,year):
            i = 0
            j = [f'player{n}',f'player{n}_pos',f'player{n}YR']
            for x in [name,position,year]:
                if x: # check if a value exits already, if so pass
                    stat_values[j[i]] = x
                    try:
                        type(int(x))
                        stat_values['player{n}_pos'],stat_values['player{n}YR'] = confirm_position(name,position,year)
                    except:
                        pass
                else: # find the empty values and replace with the session values
                    #user selection dictates how these empty values are replaced
                    stat_values[j[i]] = default_values[j[i]]
                i+=1

        ### check if page is newly loaded - load default values if so
        l = [1 if x else 0 for x in [name,position,year]]
        if sum(l):
            pass
        else:
            if n == '2':
                k = 1
            else:
                k = 0
            position = 'forwards'
            name = get_best_eleven(position,n=k)
            year = '2021'
        if n == '1':
            # check if user selects defender or keeper; if so switch players to only that selected position
            if (position.lower() in ['forwards','midfielders']) & (refresh_check == 1):
                if ([name,position,year]) == ([default_values['player1'],default_values['player1_pos'],default_values['player1YR']]):
                    pass
                else:
                    stat_values['player1_pos'] = position
                    stat_values['player1YR'] =  default_values['player1YR']#str(current_year-1)
                    stat_values['player1'] = get_best_eleven(position,n=0)
                    if stat_values['player2_pos'] in ['defenders','keepers']:
                        stat_values['player2_pos'] = position
                        stat_values['player2YR'] = str(current_year-1)
                        stat_values['player2'] = get_best_eleven(position,n=1)
                    else:
                        pass
            elif (position.lower() in ['defenders','keepers']) & (position != stat_values['player2_pos']):
                stat_values['player1_pos'] = position
                stat_values['player1YR'] = str(current_year-1)
                stat_values['player1'] = get_best_eleven(position,n=0)
                stat_values['player2_pos'] = position
                stat_values['player2YR'] = str(current_year-1)
                stat_values['player2'] = get_best_eleven(position,n=1)
            else:
                loop_data(name,position,year)
        else:
            if (position.lower() in ['forwards','midfielders']) & (refresh_check == 1):
                if ([name,position,year]) == ([default_values['player2'],default_values['player2_pos'],default_values['player2YR']]):
                    pass
                else:
                    print(f"HERE WE ARE TRYING TO GET A NEW POSITION {stat_values['player2'],stat_values['player2_pos'],stat_values['player2YR']}")
                    stat_values['player2_pos'] = position
                    stat_values['player2YR'] = str(current_year-1)
                    stat_values['player2'] = get_best_eleven(position,n=1)
            else:
                loop_data(name,position,year)

    if [stat_values['player1'],stat_values['player1_pos'],stat_values['player1YR']] == [default_values['player1'],default_values['player1_pos'],default_values['player1YR']]:
        print(f'P1 == DEFAULT & RC: {refresh_check}')
        check_choice(stat_values['player1'],stat_values['player1_pos'],stat_values['player1YR'])
    else:
        check_choice(stat_values['player1'],stat_values['player1_pos'],stat_values['player1YR'])

    if [stat_values['player2'],stat_values['player2_pos'],stat_values['player2YR']] == [default_values['player2'],default_values['player2_pos'],default_values['player2YR']]:
        print(f'P2 == DEFAULT & RC: {refresh_check}')
        check_choice(stat_values['player2'],stat_values['player2_pos'],stat_values['player2YR'],n='2')
    else:
        check_choice(stat_values['player2'],stat_values['player2_pos'],stat_values['player2YR'],n='2')

    stat_values['player1_pos'],stat_values['player1YR'] = confirm_position(stat_values['player1'],stat_values['player1_pos'],stat_values['player1YR'])
    stat_values['player2_pos'],stat_values['player2YR'] = confirm_position(stat_values['player2'],stat_values['player2_pos'],stat_values['player2YR'])

    stat_values['player1'] = player_names[stat_values['player1']]
    stat_values['player2'] = player_names[stat_values['player2']]

    print('\nFINAL P1 VALUES: ',stat_values['player1'],stat_values['player1_pos'],stat_values['player1YR'])
    print('FINAL P2 VALUES: ',stat_values['player2'],stat_values['player2_pos'],stat_values['player2YR'],'\n')

    # Generate player profile date for the player info boxes
    ###################################################################
    def get_player_information(name,year,position):
        print(f"\n{name}\n{year}\n")
        for col in ['name','display']:
            player_stat_list = stat_lists[position[:1]+'_'+str(year)][stat_lists[position[:1]+'_'+str(year)][col] == name]
            if player_stat_list.empty:
                player_stat_list = stat_lists[position[:1]+'_'+str(year)][stat_lists[position[:1]+'_'+str(year)][col].str.contains(name.split(' ')[-1])]
            if player_stat_list.empty:
                pass
            else:
                break

        check = 0
        get_pos = {'d':'defenders','f':'forwards','g':'keepers','m':'midfielders'}
        get_colour = {'Atlético Ottawa' : 'cpl-ato',
                    'Cavalry FC' : 'cpl-cfc',
                    'FC Edmonton' : 'cpl-fce',
                    'Forge FC' : 'cpl-ffc',
                    'HFX Wanderers FC' : 'cpl-hfx',
                    'Pacific FC' : 'cpl-pfc',
                    'Valour FC' : 'cpl-vfc',
                    'York United FC' : 'cpl-yor',
                    'York9 FC' : 'cpl-y9'}

        def get_player_details(year):
            for col in ['name','display']:
                player = player_info[year][player_info[year][col] == name]
                if player.empty:
                    player = player_info[year][player_info[year][col].str.contains(name.split(' ')[-1])]
                if player.empty:
                    pass
                else:
                    break

            player = player.reset_index(drop=True)
            for c,r in player.iterrows():
                flag = r['flag']
                image = r['image']
                position = get_pos[r['position']]
                number = r['number']
                team = r['team']
                colour = get_colour[team]
                display = r['display']
                overall = player_stat_list['overall'].values[0]
                min = player_stat_list['Min'].values[0]
                try:
                    special1 = player_stat_list['Int'].values[0]
                except:
                    try:
                        special1 = player_stat_list['CleanSheet'].values[0]
                    except:
                        special1 = player_stat_list['ExpG'].values[0]
                try:
                    special2 = player_stat_list['Clrnce'].values[0]
                except:
                    try:
                        special2 = player_stat_list['Saves'].values[0]
                    except:
                        special2 = player_stat_list['ExpA'].values[0]
            print(flag,image,position,number,team,colour,display,overall,min,special1,special2)
            return flag,image,position,number,team,colour,display,overall,min,special1,special2


        player_information = {}
        try:
            player_information['flag'],player_information['image'],player_information['position'],player_information['number'],player_information['team'],player_information['colour'],player_information['display'],player_information['overall'],player_information['min'],player_information['special1'],player_information['special2'] = get_player_details(year)
        except:
            # maybe the player didn't play that year, otherwise try the next year
            if year == '20':
                year = '19'
            else:
                year = '20'
            try:
                player_information['flag'],player_information['image'],player_information['position'],player_information['number'],player_information['team'],player_information['colour'],player_information['display'],player_information['overall'],player_information['min'],player_information['special1'],player_information['special2'] = get_player_details(year)
                check = year
            except:
                player_information['flag'],player_information['image'],player_information['position'],player_information['number'],player_information['team'],player_information['colour'],player_information['display'],player_information['overall'],player_information['min'],player_information['special1'],player_information['special2'] = get_player_details(year)
                check = year

        if player_information['position'] in ['goal keeper','goal keepers']:
            player_information['position'] = 'keeper'
        return player_information, check


    player1_information,check = get_player_information(stat_values['player1'],stat_values['player1YR'][2:],stat_values['player1_pos'])
    if check:
        stat_values['player1YR'] = '20'+check

    player2_information,check = get_player_information(stat_values['player2'],stat_values['player2YR'][2:],stat_values['player2_pos'])
    if check:
        stat_values['player2YR'] = '20'+check

    print(player2_information)

    ############## get position line function
    def get_position_line(data,year=current_year,position='defenders',name=''):
        if name:
            if type(year) != str:
                year = str(year)
            string = f'{position[:1]}_{year[2:]}_l'
            for col in ['name','display']:
                      df = data[string][data[string][col]== name]
                      if df.empty:
                          df = data[string][data[string][col].str.contains(name.split(' ')[-1])]
                      if df.empty:
                          pass
                      else:
                          break
            for col in ['name','display']:
                try:
                    min_div = round(stat_lists[string[:4]][stat_lists[string[:4]][col]== name]['Min'].values[0]/90,2)
                except:
                    try:
                        min_div = round(stat_lists[string[:4]][stat_lists[string[:4]][col].str.contains(name.split(' ')[-1])]['Min'].values[0]/90,2)
                    except:
                        pass
            return df, min_div
        else:
            print('ERROR: requires name=<player name>')
    ############## END OF get position line function

    player_1_line,min_div1 = get_position_line(stat_lines,year=stat_values['player1YR'],position=player1_information['position']+'s',name=stat_values['player1'])
    player_2_line,min_div2 = get_position_line(stat_lines,year=stat_values['player2YR'],position=player2_information['position']+'s',name=stat_values['player2'])

    #### Can't currently Compare player to himself!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    ##################################################################################################################
    ############## compare_two lines function
    def compare_two(q1,min1,db,q2,min2,df,column='Goal'):

        if q1==q2:
            q1='t1'
            q2='t2'

        def get_norm(data,min_d):
            df = data.copy()
            cols = [x for x in data.columns if x not in ['team','name','display','Goal','CleanSheet']]
            for col in cols:
                df[col] = round(df[col]/ min_d ,2)
            return df

        # compare the shapes of the dataframes - require similar length
        # take the shortest one
        compare = pd.DataFrame()
        if db.shape[0] > df.shape[0]:
            c = df.shape[0]
        else:
            c = db.shape[0]

        db = get_norm(db,min1)
        df = get_norm(df,min2)

        compare[q1] = db[column].head(c).tolist() # played one more game that season
        compare[q2] = df[column].head(c).tolist()

        return compare
    ############## END OF compare_two lines function

    col_choices = [x for x in list(set(player_1_line.columns.values.tolist()).intersection(player_2_line.columns.values.tolist())) if x not in ['team','name','display']]

    plot_values = {'d':['Goal','Clrnce','Int','SucflTkls'],
               'f':['Goal','TchsA3','PsOpHfFl','PsCmpA3'],
               'k':['CleanSheet','BgChncFace','Saves','SvDive'],
               'm':['Goal','TchsA3','PsOpHfFl','PsCmpA3']}

    results = {}
    for x in plot_values[player1_information['position'][:1]]:
        results[x] = compare_two(stat_values['player1'],min_div1,player_1_line,stat_values['player2'],min_div1,player_2_line,column=x)

    if player_1_line[plot_values[player1_information['position'][:1]][0]].max() > player_2_line[plot_values[player1_information['position'][:1]][0]].max():
        multiplier = player_1_line[plot_values[player1_information['position'][:1]][0]].max()
    else:
        multiplier = player_2_line[plot_values[player1_information['position'][:1]][0]].max()
    if multiplier == 0:
        multiplier = 1

    player_lines, line_columns = [], []
    for x in results:
        line_columns.append(x)
        player_lines.append(results[x].T.values.tolist())

    colour_dict = { 'cpl-ato':'#102f52','cpl-cfc':'#3b7324','cpl-fce':'#004C97','cpl-ffc':'#DE4405','cpl-hfx':'#41B6E6','cpl-pfc':'#582C83','cpl-vfc':'#b9975b','cpl-yor':'#046a38','cpl-y9':'#78BE20'}

    colour1 = colour_dict[player1_information['colour']]
    colour2 = colour_dict[player2_information['colour']]

    if (colour1 == '#3b7324') & (colour2 == '#78BE20'):
        colour1 = '#DA291C'
    if (colour2 == '#78BE20') & (colour2 == '#3b7324'):
        colour2 = '#DA291C'
    if (colour1 == '#102f52') & (colour2 == '#004C97'):
        colour1 = '#E4002B'
    if (colour2 == '#004C97') & (colour2 == '#102f52'):
        colour2 = '#E4002B'

    def change_hex(col, amt):
        vals = tuple(int(col.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        g,b,r = vals[0]+amt, vals[1]+amt, vals[2]+int(amt/2)
        new_col = '#%02x%02x%02x' % (g,r,b)
        return str(new_col)

    if colour1 == colour2:
        colour2 = change_hex(colour2,40)
        if len(colour2) > 7:
            colour2 = colour2[:7]

    col_change = {'CleanSheet':'Clean Sheets',
                'BgChncFace':'Big Chances Faced',
                'Goal':'Goals',
                'PsCmpA3':'Passes Completed Attacking 3rd',
                'Clrnce':'Clearances',
                'Int':'Interceptions',
                'SucflTkls':'Successful Tackles',
                'PsOpHfFl':'Successful Passes Opponents Half',
                'Saves':'Saves',
                'SvDive': 'Diving Saves',
                'TchsA3':'Touches Attacking 3rd'}

    line_columns = [col_change[x] for x in line_columns]

    session['player1_pos'] = stat_values['player1_pos']
    session['player1'] = stat_values['player1']
    session['player1YR'] = stat_values['player1YR']
    session['player2_pos'] = stat_values['player2_pos']
    session['player2'] = stat_values['player2']
    session['player2YR'] = stat_values['player2YR']

    player1_select_list = sorted(stat_lists[f'{stat_values["player1_pos"][:1].lower()}_{stat_values["player1YR"][2:]}']['name'].unique().tolist().copy())
    if stat_values['player1'] in player1_select_list:
        player1_select_list.remove(stat_values['player1'])
    else:
        pass

    player2_select_list = sorted(stat_lists[f'{stat_values["player2_pos"][:1].lower()}_{stat_values["player2YR"][2:]}']['name'].unique().tolist().copy())
    if stat_values['player2'] in player2_select_list:
        player2_select_list.remove(stat_values['player2'])
    else:
        pass

    colour1 = '#caf0f8'#'#fff1d0'
    colour2 = '#001219'#'#003b5c'

    return render_template('player-compare.html', geegle = geegle, headline= headline,
    player1_select_list = player1_select_list, player2_select_list = player2_select_list,
    player1_team = player1_information['team'], player1_colour = player1_information['colour'],
    player1_flag = player1_information['flag'], player1_image = player1_information['image'],
    player1_num = player1_information['number'], player1_pos = player1_information['position'],
    player1_min = player1_information['min'], player1_over = player1_information['overall'],
    player1_special1 = player1_information['special1'], player1_special2 = player1_information['special2'],
    player2_team = player2_information['team'], player2_colour =player2_information['colour'],
    player2_flag = player2_information['flag'], player2_image = player2_information['image'],
    player2_num = player2_information['number'], player2_pos = player2_information['position'],
    player2_min = player1_information['min'], player2_over = player2_information['overall'],
    player2_special1 = player1_information['special1'], player2_special2 = player2_information['special2'],
    p1_year = stat_values['player1YR'], p2_year = stat_values['player2YR'],
    player_names = [player1_information['display'],player2_information['display']], chart_team_colour_list = [colour1, colour2],
    player_line = player_lines[0],line_columns = line_columns,
    player_line_2 = player_lines[1],player_line_3 = player_lines[2],player_line_4 = player_lines[3],
    colour1 = colour1,colour2 = colour2,colour3 = geegle[2])

@canpl.route('/player', methods=['GET','POST'])
def player():

    year, error = get_year()

    # temporary fix for no data
    db_chk = pd.read_csv(f'datasets/{current_year}/playerstats/{current_year}-forwards.csv')
    db_chk = db_chk.loc[0]['name']
    if year == current_year and db_chk.lower() == 'tbd':
        year = str(int(current_year)-1)

    team_ref = pd.read_csv('datasets/teams.csv')
    team_ref = team_ref[team_ref['year'] == int(year)]

    name = request.form['name']

    if name in player_names_df['name'].unique():
        print('NAME: present',name)
        try:
            display = player_names_df[player_names_df['name'] == name]['display'].values[0]
            print('DISPLAY: ',display)
        except Exception as e:
            print('DISPLAY: not found')
            print('ERROR: ',e)
    elif name in player_names_df['display'].unique():
        print('NAME: not present DISPLAY: ',name)
        display = name
        try:
            name = player_names_df[player_names_df['display'] == display]['name'].values[0]
            print('NAME: found',name)
        except Exception as e:
            print('DISPLAY: not found')
            print('ERROR: ',e)
    else:
        print('ERROR')
        print(player_names_df['name'].unique())


    print(f'{name} and {display}')

    year_list = player_info['year'].unique().tolist()
    active_years = []
    for yr in year_list:
        check = 0
        df = player_info[(player_info['name'] == name) & (player_info['year'] == yr)]
        if df.empty:
            pass
        else:
            check = 1
        print(check,yr)
        if check:
            active_years.append(yr)

    k = year_list.index(year)

    print('SEARCHING YEAR: ',year)

    player = player_info[(player_info['name'] == name) & (player_info['year'] == year)]
    if player.empty:
        year_list_trim = year_list.copy()
        del year_list_trim[k]
        print('SEARCHING YEAR: ',year_list_trim[0])
        year = year_list_trim[0]
        player = player_info[(player_info['name'] == name) & (player_info['year'] == year_list_trim[0])]
        if player.empty:
            print('SEARCHING YEAR: ',yyear_list_trim[1])
            year = year_list_trim[1]
            player = player_info[(player_info['name'] == name) & (player_info['year'] == year_list_trim[1])]

    print(f'player information \n{player}\n')

    team = player['team'].values[0]

    def AgeTest(dob):
        dobnew = tuple(map(int, dob.split('-')))
        age = relativedelta(date.today(), date(*dobnew))
        return age.years
    age = AgeTest(player['dob'].values[0])

    colour3 = team_colour[team]
    roster_team_info = team_ref[team_ref['team'] == team]
    roster_colour = roster_team_info.iloc[0][4]
    crest = roster_team_info.iloc[0]['crest']
    colour1 = roster_team_info.iloc[0]['colour1']
    colour2 = roster_team_info.iloc[0]['colour2']
    pos = player['position'].values[0]
    position = {'d':'defenders','f':'forwards','g':'keepers','m':'midfielders'}
    selected_position = pd.read_csv(f'datasets/{year}/playerstats/{year}-{position.get(pos)}.csv')
    print(f'ALL PLAYERS at position \n{selected_position}\n')

    min_divisor = round(selected_position['Min'].values[0]/90,2)
    selected_position_90 = pd.read_csv(f'datasets/{year}/playerstats/{year}-{position.get(pos)}90.csv')
    discipline = pd.read_csv(f'datasets/{year}/playerstats/{year}-discipline.csv')

    db = selected_position[selected_position['name'] == name].reset_index(drop=True)
    if db.empty:
        print('\n*************EMPTY*************\n')
        db = selected_position[selected_position['name'] == display].reset_index(drop=True)
    print('CHECKING FOR ERRORS******************')
    print(f'QUERIED PLAYER AT position \n{db}\n')

    db90 = selected_position_90[selected_position_90['name'] == name].reset_index(drop=True)
    if db90.empty:
        db90 = selected_position_90[selected_position_90['name'] == display].reset_index(drop=True)

    def new_col(data):
        for col in data.columns:
            try:
                data = data.rename(columns={col:col_check[col]})
            except:
                pass
        '''temp = {}
        for col in data.columns:
            try:
                if col in ['display','number']:
                    temp[col] = data.pop(col)
            except:
                pass
        data['display'] = temp['display']
        data['number'] = temp['number']'''
        return data

    print(f'\n THEN\n{db}\n')
    print(f'\n{player}\n')

    db = new_col(db)
    db90 = new_col(db90)

    # temporary fix for issue
    for x in db.columns:
        if x in ['shtTrg','Pfa']:
            db.pop(x)

    if db['name'].values[0] != player['name'].values[0]:
        db.at[0,'name'] = player['name'].values[0]

    print(f'\n NOW\n{db}\n')

    radar_chart = db.copy()
    radar_chart.pop('display')
    radar_chart = new_col(radar_chart)
    for col in radar_chart.columns[5:-1]:
        radar_chart[col] = round((radar_chart[col] / (radar_chart[col].max()+0.05)),2)
    radar_chart = radar_chart[radar_chart['name'] == name][radar_chart.columns[6:-1]]
    radar_chart = cpl_main.index_reset(radar_chart)
    radar_chart_cols = "'"+"', '".join(radar_chart.columns)+"'"

    player_discipline = discipline[discipline['name'] == name]
    if player_discipline.empty:
        player_discipline = discipline[discipline['display'] == name]


    if db.empty:
        print('Stats Empty')

        db = pd.read_csv(f'datasets/{year}/playerstats/{year}-{position.get(pos)}.csv')
        db = db.min()
        db = cpl_main.index_reset(db)
        for col in db.select_dtypes(include=np.number).columns:
            db[col] = 0
        db['Min'] = 0

        radar_chart = db.copy()
        radar_chart = radar_chart[radar_chart.columns[6:-1]]
        radar_chart_cols = "'"+"', '".join(radar_chart.columns)+"'"

        discipline = pd.read_csv(f'datasets/{year}/playerstats/{year}-discipline.csv')
        discipline = discipline.min()
        discipline = cpl_main.index_reset(discipline)
        for col in discipline.select_dtypes(include=np.number).columns:
            db[col] = 0

        details = {}
        for word in ['display','number','nationality','team']:
            try:
                details[word] = player[player['display'] == name][word].values[0]
            except:
                sleep(1)
                details[word] = player[player['name'] == name][word].values[0]

        player_line = [[0.0, 0.0, 0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]]

        return render_template('player.html', year = year, age = age, name = details['display'], player_line_length = 1, player_line_end = 1,active_years = active_years,
        nationality = details['nationality'], team_name = team, player_info = player, full_name = name,
        team_colour = roster_colour, crest = crest, position = position.get(pos)[:-1], number = details['number'], chart_team_colour_list = geegle,
        stats = db, stats90 = db, discipline = discipline, radar_chart = radar_chart, radar_chart_cols = radar_chart_cols,
        colour1 = colour1, colour2 = colour2, colour3 = colour3, col_nums = [0,5], player_line = player_line,line_columns = ['NA','NA','NA','NA','NA','NA'])

    player_line_db = pd.read_csv(f'datasets/{year}/playerstats/{year}-{position.get(pos)}-line.csv')
    try:
        player_line_db = player_line_db[['name','display','Touches','Goal','PsAtt','PsCmpM3','TchsM3']]
    except:
        try:
            player_line_db = player_line_db[['name','display','Touches','Goal','PsAtt','TchsA3']]
        except:
            try:
                player_line_db = player_line_db[['name','display','Touches','Goal','TchsM3','DefTouch']]
            except:
                player_line_db = player_line_db[['name','display','CleanSheet','Saves','SvDive','Recovery','ExpGAg']]

    if name in player_line_db['name'].unique():
        print('NAME: found')
        player_line_df = player_line_db[player_line_db['name'] == name].copy()
        player_line_df = new_col(player_line_df)
    else:
        print('NAME: not found')
        if display in player_line_db['name'].unique():
            print('DISPLAY NAME: found')
            player_line_df = player_line_db[player_line_db['name'] == display].copy()
            player_line_df = new_col(player_line_df)

        else:
            try:
                print('DISPLAY NAME: search by last name')
                player_line_df = player_line_db[player_line_db['name'].str.contains(display.split(' ')[-1])].copy()
                player_line_df = new_col(player_line_df)
            except:
                print('DISPLAY: not found')
                player_line_df = pd.DataFrame([[name,0,0,0,0,0,display],
                                               [name,0,0,0,0,0,display],
                                               [name,0,0,0,0,0,display]],columns=(['name','tch','b','c','d','e','display']))

    def get_norm(data):
        df = data.copy()
        cols = [x for x in data.columns if x not in ['name','display','G','CS']]
        for col in cols:
            df[col] = round(df[col]/ min_divisor ,2)
        if 'CS' in data.columns:
            mod = [df['SV'].max(),df['Rec'].max()]
            df['CS'] = df['CS'] * max(mod)
        return df

    player_line_df = get_norm(player_line_df)

    def percentage_check(x):
        try:
            if '%' in x:
                return float(re.sub('%','',x))
            elif '-' in x:
                return 0.0
        except:
            return x

    def build_player_line(data,display):
        df = cpl_main.index_reset(data).copy()
        if 'G' in df.columns.values:
            g = df.pop('G')
            df.insert(1,'G',g)
        # get the columns headers

        # pop out the name related columns
        for col in ['name','display']:
            df.pop(col)
        # get rid of any string symbols such as % and convert to float if needed
        for col in df.columns:
            df[col] = df[col].apply(lambda x: percentage_check(x))

        line_columns = [x for x in df.columns]

        return df.T, line_columns

    player_line, line_columns = build_player_line(player_line_df,display)
    player_line = player_line.values.tolist()
    player_line_length = len(player_line) - 1
    player_line_end = len(player_line) - 1

    if player_line[0]:
        print('DATASET: filled')
    else:
        print('ERROR:')
        print('DATASET: empty')

    details = {}
    for word in ['display','number','nationality','team']:
        try:
            details[word] = player[player['display'] == name][word].values[0]
        except:
            details[word] = player[player['name'] == name][word].values[0]

    if position.get(pos)[:1] == 'f':
        length = len(db.columns)
        half = int(length/2)
        full = int(len(db.columns) - 2)
        col_nums = [half,full]
    else:
        length = len(db.columns)
        half = int(length/2)
        full = int(len(db.columns) - 2)
        col_nums = [half,full]


    col_change = {'CS':'Clean Sheet',
                'defTch':'Defensive Touches',
                'G':'Goals',
                'xGc':'Expected Goals Against',
                'Pat':'Passes Attempted',
                'Patm':'Passes Completed Middle 3rd',
                'Rec':'Recoveries',
                'dvS':'Diving Saves',
                'SV':'Saves',
                'Tcha':'Touches Attacking 3rd',
                'Tchm':'Touches Middle 3rd',
                'Tch':'Touches'}

    column_names = [col_change[x] for x in line_columns]

    display_year = year

    print(radar_chart)
    print(player_line)

    return render_template('player.html', year = year, age = age, name = details['display'], player_line_length = len(player_line)-1, player_line_end = player_line_end,
    nationality = details['nationality'], team_name = team, player_info = player, full_name = name, column_names = column_names,active_years = active_years,
    team_colour = roster_colour, crest = crest, position = position.get(pos)[:-1], number = details['number'], chart_team_colour_list = geegle,
    stats = db, stats90 = db90, discipline = discipline, radar_chart = radar_chart, radar_chart_cols = radar_chart_cols,
    colour1 = colour1, colour2 = colour2, colour3 = colour3, col_nums = col_nums, player_line = player_line,line_columns = line_columns)

@canpl.route('/goals', methods=['GET','POST'])
def goals():
    # load goals and assists leaderboards
    year, error = get_year()
    # import the csv file and read as a pandas dataframe
    rated_goalscorers = pd.read_csv(f'datasets/{year}/playerstats/{year}-goalscorers.csv')
    headline = 'Top 10 Goals / Assists for '
    if rated_goalscorers.at[0,'team'] == 'tbd':
        check = 1
        last_year = str(int(year)-1)
        rated_goalscorers = pd.read_csv(f'datasets/{last_year}/playerstats/{last_year}-goalscorers.csv')
        headline = 'Top 10 Goals / Assists from '
        year = last_year
    rated_assists = pd.read_csv(f'datasets/{year}/playerstats/{year}-assists.csv')
    if rated_assists.at[0,'team'] == 'tbd':
        check = 1
        last_year = str(int(year)-1)
        rated_assists = pd.read_csv(f'datasets/{last_year}/playerstats/{last_year}-assists.csv')
    # only take the top 10 from each leaderboard
    rated_g10 = rated_goalscorers.head(10)
    rated_a10 = rated_assists.head(10)
    # get the columns from the leaderboards
    columns_g = rated_goalscorers.columns
    columns_a = rated_assists.columns

    return render_template('goals.html',columns_g = columns_g, columns_a = columns_a, year = year,
    html_table = rated_g10, assists_table = rated_a10, headline = headline)

@canpl.route('/<pos>', methods=['GET','POST'])
def position(pos):
    # load position leaderboards
    year, error = get_year()
    check = 0
    # import the csv file and read as a pandas dataframe
    rated_position = pd.read_csv(f'datasets/{year}/playerstats/{year}-{pos}.csv')
    rated_position = rated_position[rated_position['Min']>0]
    print(rated_position.columns)
    print(rated_position)
    # check if the dataframe has relevant data that can be used
    # if not, load previous years data
    if rated_position.at[0,'team'] == 'tbd':
        check = 1
        last_year = str(int(year)-1)
        rated_position = pd.read_csv(f'datasets/{last_year}/playerstats/{last_year}-{pos}.csv')
    columns = rated_position.columns

    #tooltip = {v:k for k,v in col_check.items()}

    rated_position = new_col(rated_position)

    return render_template('position.html', year = year, position_link = pos,
    tooltip = tooltip,
    columns = columns,html_table = rated_position,check = check)

@canpl.route('/<pos>P90', methods=['GET','POST'])
def position90(pos):
    # load position per 90 leaderboards
    year, error = get_year()
    check = 0
    # import the csv file and read as a pandas dataframe
    rated_position_90 = pd.read_csv(f'datasets/{year}/playerstats/{year}-{pos}90.csv')
    rated_position_90 = rated_position_90[rated_position_90['Min']>0]
    # check if the dataframe has relevant data that can be used
    # if not, load previous years data
    if rated_position_90.at[0,'team'] == 'tbd':
        check = 1
        last_year = str(int(year)-1)
        rated_position_90 = pd.read_csv(f'datasets/{last_year}/playerstats/{last_year}-{pos}90.csv')
    rated_position = rated_position_90.sort_values(by='overall',ascending=False)
    columns = rated_position.columns

    rated_position = new_col(rated_position)

    return render_template('position.html', year = year, position_link = pos,
    columns = columns,html_table = rated_position,check = check)

@canpl.route('/discipline', methods=['GET','POST'])
def discipline():
    # load displine leaderboards
    year, error = get_year()
    # import the csv file and read as a pandas dataframe
    rated_offenders = pd.read_csv(f'datasets/{year}/playerstats/{year}-discipline.csv')
    # check if the dataframe has relevant data that can be used
    # if not, load previous years data
    if rated_offenders['Yellow'].max() == 0:
        pass
    else:
        rated_offenders = rated_offenders[(rated_offenders['Yellow'] > 0) | (rated_offenders['Red'] > 0)]
    rated_offenders = rated_offenders.sort_values(by=['Red','2ndYellow','Yellow'], ascending = False)
    columns = rated_offenders.columns

    return render_template('discipline.html',columns = columns, year = year,
    html_table = rated_offenders, headline = 'Discipline')

@canpl.route('/blog', methods=['GET','POST'])
def blog():
    year, error = get_year()

    # directory to search for sub directories and files
    path ='datasets/blog/2021/'
    # dictionary to store all the files found

    with os.scandir(path) as files:
        gathered = {}
        for file in files:
            text = open(path+file.name, 'r')

            gathered[file.name] = {
            'author': contributors[file.name[-7:-4]],
            'date': f'{file.name[:2]}-{file.name[2:4]}-2021',
            'title': f'{file.name[5:-11].title()}',
            'article': text.read(),
            }

    articles = {}

    for k in reversed(sorted(gathered.keys())):
        articles[k] = gathered[k]

    return render_template('blog.html',headline = 'Contributors Blog',year = year,articles = articles)

@canpl.route('/article_<title>', methods=['GET','POST'])
def article(title):
    year, error = get_year()
    # directory to search for sub directories and files
    path ='datasets/blog/2021/'

    with os.scandir(path) as files:
        articles = {}
        for file in files:
            text = open(path+file.name, 'r')

            articles[file.name] = {
            'author': contributors[file.name[-7:-4]],
            'date': f'{file.name[:2]}-{file.name[2:4]}-2021',
            'title': f'{file.name[5:-11].title()}',
            'article': text.read(),
            }
    index_list = [x for x in sorted(articles.keys())]

    for k in sorted(articles.keys()):
        if title.lower() in k.lower():
            x = index_list.index(k)
            y,z = x-1,x+1
            team = k[-10:-7]
            article = articles[k]

    print(f'\n{x,y,z}\n')
    try:
        previous = 'article_'+index_list[y][5:-11].title()
    except:
        previous = 'blog'

    try:
        next = 'article_'+index_list[z][5:-11].title()
    except:
        next = 'blog'

    print(previous,next)

    return render_template('article.html',headline = 'Contributors Blog',year = year,
    previous = previous, next = next,
    article = article,team = team)

@canpl.route('/feed', methods=['GET','POST'])
def feed():
    year, error = get_year()
    return render_template('feed.html')

@canpl.errorhandler(werkzeug.exceptions.BadRequest)
def handle_bad_request(e):
    return 'bad request!', 400

@canpl.route('/error')
def error():
    return render_template('error.html')

@canpl.route('/googledaf818200d6bdf9d.html')
def google():
    return render_template('googledaf818200d6bdf9d.html')

@canpl.route('/hell')
def hello():
    return 'Welcome to HELL world!'

if __name__ == "__main__":
    canpl.run()
