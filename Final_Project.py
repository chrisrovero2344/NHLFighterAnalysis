#Import Required Packages
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright, Playwright
import re
import requests
import pandas as pd
import time
import json
import random
import numpy as np

#Set Variables for Years of Interest and Arbitrary Page Numbers as Some Years Go Up to 80 Pages

year_list = list(range(2000,2027))

page_number = list(range(1,90))
page_number

#Cheat the 404 Error
headers = {'User-Agent':'Mozilla 5.0'}

df = []

#Nested For Loop Iterating Over the Years and Pages to Remove List of Fights on Each Page
for year in year_list:
    for page in page_number:
        hockey_fights_link = f'https://www.hockeyfights.com/fightlog/1/reg{year}/{page}'
        time.sleep(0.8)
        print(f'https://www.hockeyfights.com/fightlog/1/reg{year}/{page}')

        fights_link_request = requests.get(hockey_fights_link, headers=headers)
        if hockey_fights_link == "404":
            continue

        fight_content = fights_link_request.text
        if "No fights for these parameters" in fight_content:
            continue
        print(fight_content)

        hockey_soup = BeautifulSoup(fight_content)

        fighters = hockey_soup.select(".text-xl")
        fighters = [x.text.strip() for x in fighters]

        #We Also Receive Watch in Our List of Winners, Must Remove
        winner = hockey_soup.select(".underline.underline-offset-2")
        winner = [x.text.strip() for x in winner]
        winner = [w for w in winner if w.lower() != "watch"]
        
        rating_text = hockey_soup.select(".flex.flex-col.justify-between.gap-2")
        rating_text = [x.text.strip() for x in rating_text]
        #rating_text = [x.get_text(strip=True) for x in rating_text]
    
        ratings = []
        vote_counts = []
        full_date = []

        #RegEx Match the Rest of Information from rating_text (Probably Could Have Started Here LOL)
        for text in rating_text:
            rating_match = re.search(r"Voted rating:\s*([0-9]+(?:\.[0-9]+)?)", text)
            vote_match = re.search(r"Vote count:\s*(\d+)", text)
            date_match = re.search(r"\d{2}/\d{2}/\d{2}", text)
            ratings.append(float(rating_match.group(1)) if rating_match else None)
            vote_counts.append(int(vote_match.group(1)) if vote_match else None)
            full_date.append(date_match.group(0) if date_match else None)

        output = pd.DataFrame({
            "season": year,
            "full_date": full_date,
            "fighters": fighters,
            "winner": winner,
            "rating": ratings,
            "votes": vote_counts
            })

        df.append(output)


#Move into DataFrame and Drop as Many Blank Values as Possible, Assuming There is No List of 10 Fighter Strings That Exactly Match
original_extraction = pd.concat(df)
original_data_extract = pd.DataFrame(original_extraction)
original_data_extract

exploded_df = original_data_extract
exploded_df

#Separating Out Information for Fighter 1
exploded_df['Fighter 1 Name'] = exploded_df['fighters'].str.extract(r'^(\w\.\s\w+)')
exploded_df['Fighter 1 Name'] = exploded_df['Fighter 1 Name'].str.replace(r' ','', regex=True)
exploded_df['Fighter 1 Team'] = exploded_df['fighters'].str.extract(r'(?=\((\w+))')
exploded_df

#Separating Out Information for Fighter 2
exploded_df['Fighter 2 Full'] = exploded_df['fighters'].str.extract(r'((?<=vs.).*)')
exploded_df['Fighter 2 Name'] = exploded_df['Fighter 2 Full'].str.extract(r'^(\s\w\.\s\w+)')
exploded_df['Fighter 2 Name'] = exploded_df['Fighter 2 Name'].str.replace(r' ','', regex=True)
exploded_df['Fighter 2 Team'] = exploded_df['Fighter 2 Full'].str.extract(r'(\(.*)')
exploded_df['Fighter 2 Team'] = exploded_df['Fighter 2 Team'].str.extract(r'(\w+)')
exploded_df

#Save Our Extracted DataFrame
pd.DataFrame.to_csv(exploded_df,r'C:\Users\chris\OneDrive\Desktop\Notre Dame\Spring 2026 - Mod 3\Networks Theory and Analysis\fight_list_complete.csv')

#Import Our Extracted DataFrame as fight_list
fight_list = pd.read_csv(r'C:\Users\chris\OneDrive\Desktop\Notre Dame\Spring 2026 - Mod 3\Networks Theory and Analysis\fight_list_complete.csv')
fight_list

#We Have to Overwrite Names from Scraping to Match Roster Pull
fight_list['Fighter 1 Name'] = fight_list['fighters'].str.extract(r'^(\w\.\s\w\'\w+|\w\.\s\w+-\w+|\w\.\s\w+\,\w+|\w\.\s\w+)')
fight_list['Fighter 1 Name'] = fight_list['Fighter 1 Name'].str.replace(r'\,','',regex=True)
fight_list['Fighter 1 Name'] = fight_list['Fighter 1 Name'].str.replace(r'\s','',regex=True)
fight_list['Fighter 2 Name'] = fight_list['Fighter 2 Full'].str.extract(r'^(\s\w\.\s\w+-\w+|\s\w\.\s\w+\,\w+|\s\w\.\s\w+)')
fight_list['Fighter 2 Name'] = fight_list['Fighter 2 Name'].str.replace(r' ','', regex=True)
fight_list['Fighter 2 Name'] = fight_list['Fighter 2 Name'].str.replace(r'\,','',regex=True)
fight_list
test = fight_list
test
pd.DataFrame.to_csv(test,r'C:\Users\chris\OneDrive\Desktop\Notre Dame\Spring 2026 - Mod 3\Networks Theory and Analysis\test.csv')

#Set Up Variables to Work on Divisions and Conferences 
divisions = {'Atlantic':('TBL','MTL','DET','BUF','BOS','OTT','TOR','FLA'),
    'Metropolitan':('CAR','PIT','NYI','NYR','NJD','WSH','CBJ','PHI'),
    'Central':('COL','MIN','DAL','UTA','NSH','WPG','STL','CHI'),
    'Pacific':('VGK','CGY','SEA','ANA','VAN','EDM','LAK','SJS'),
    'No Division':('ATL','ARI','PHX')}

conferences = {"Western":('Central', 'Pacific'),
               "Eastern":('Atlantic','Metropolitan'),
               "No Conference":('No Division',)}

#Invert the Dictionaries to Match Team to Division and Conference
inverted_divisions = {team: div for div, teams in divisions.items() for team in teams}

division_to_conf = {div: conf for conf, divs in conferences.items() for div in divs}
inverted_conferences = {team: division_to_conf[div] for team, div in inverted_divisions.items()}

#Lets Add the Divisions and Conferences to the DataSet
fight_list['Fighter 1 Division'] = fight_list['Fighter 1 Team'].apply(lambda x: inverted_divisions.get(x))
fight_list['Fighter 2 Division'] = fight_list['Fighter 2 Team'].apply(lambda x: inverted_divisions.get(x))
fight_list['Fighter 1 Conference'] = fight_list['Fighter 1 Team'].apply(lambda x: inverted_conferences.get(x))
fight_list['Fighter 2 Conference'] = fight_list['Fighter 2 Team'].apply(lambda x: inverted_conferences.get(x))

fight_list

#Create a Hiearchy of Overwrites Because I Cant Code for Distinguishing Fight Type for Edgelist
fight_list['Fight Type'] = 'Out-of-Conference'
fight_list.loc[fight_list['Fighter 1 Conference'] == fight_list['Fighter 2 Conference'],'Fight Type'] = 'Interconference'
fight_list.loc[fight_list['Fighter 1 Division'] == fight_list['Fighter 2 Division'],'Fight Type'] = 'Interdivision'
fight_list

#Need to Extract the Winning Percentage and Place in Its Own Column
fight_list['winning_percent'] = fight_list['winner'].str.extract(r'(\(.*\))')
fight_list['winning_percent'] = fight_list['winning_percent'].str.extract(r'(w\+|\d+)')
fight_list['winning_percent'] = fight_list['winning_percent'].astype(float)

#And We Will Remove Everything After the Winners Name and Look to Match it to Our Future Structure Needed for ID Matching
fight_list['winner'] = fight_list['winner'].str.replace(r'(\(.*\))','',regex=True)
fight_list['winner'] = fight_list['winner'].str.replace(r'^([A-Z])\.[A-Z]\.\s+', '\1. ', regex=True)
fight_list['winner'] = fight_list['winner'].str.replace(r'(^.)(\w+)','\\1.\\2',regex=True)
fight_list['winner'] = fight_list['winner'].str.replace(r'(?<=\.)(\w\'\w+|\w+-\w+\s|\w+\s)','',regex=True)
fight_list['winner'] = fight_list['winner'].str.replace(r'\s','',regex=True)

#Create a For Loop that Finds the Loser of Each Fight
losers = []
for index, row2 in fight_list.iterrows():
    if row2['winner'] == row2['Fighter 1 Name']:
        fight_loser = row2['Fighter 2 Name']
    else:
        fight_loser = row2['Fighter 1 Name']
    losers.append(fight_loser)

fight_list['fight_loser'] = losers
fight_list

#Now That We Have Winners AND Losers Lets Match Up the Team Names the Same Way!
winner_team = []
for index, row1 in fight_list.iterrows():
    if row1['winner'] == row1['Fighter 1 Name']:
        fight_winner = row1['Fighter 1 Team']
    else:
        fight_winner = row1['Fighter 2 Team']
    winner_team.append(fight_winner)
fight_list['winner_team'] = winner_team

loser_team = []
for index, row3 in fight_list.iterrows():
    if row3['fight_loser'] == row3['Fighter 1 Name']:
        fight_loser = row3['Fighter 1 Team']
    else:
        fight_loser = row3['Fighter 2 Team']
    loser_team.append(fight_loser)
fight_list['loser_team'] = loser_team

fight_list['winner_team'].value_counts()
fight_list['loser_team'].value_counts()

#Because I Didn't Think This Through We Have to Do Extra Work for Conferences and Divisons So the Edge List Attributes are for Winner/Loser
winner_conference = []
for index, row4 in fight_list.iterrows():
    if row4['winner'] == row4['Fighter 1 Name']:
        winner_conf = row4['Fighter 1 Conference']
    else:
        winner_conf = row4['Fighter 2 Conference']
    winner_conference.append(winner_conf)
fight_list['winner_conf'] = winner_conference

loser_conference = []
for index, row4 in fight_list.iterrows():
    if row4['fight_loser'] == row4['Fighter 1 Name']:
        loser_conf = row4['Fighter 1 Conference']
    else:
        loser_conf = row4['Fighter 2 Conference']
    loser_conference.append(loser_conf)
fight_list['loser_conf'] = loser_conference

winner_division = []
for index, row5 in fight_list.iterrows():
    if row5['winner'] == row5['Fighter 1 Name']:
        winner_div = row5['Fighter 1 Division']
    else:
        winner_div = row5['Fighter 2 Division']
    winner_division.append(winner_div)
fight_list['winner_div'] = winner_division

loser_division = []
for index, row6 in fight_list.iterrows():
    if row6['fight_loser'] == row6['Fighter 1 Name']:
        loser_div = row6['Fighter 1 Division']
    else:
        loser_div = row6['Fighter 2 Division']
    loser_division.append(loser_div)
fight_list['loser_div'] = loser_division

fight_list

#Export Check
test_3 = fight_list
pd.DataFrame.to_csv(test_3,r'C:\Users\chris\OneDrive\Desktop\Notre Dame\Spring 2026 - Mod 3\Networks Theory and Analysis\test_3.csv')

#Now We Need to Make an EdgeList, Lets Redefine Our Variables and Include a Player ID to Make Concat Simple
fighter_1 = fight_list['winner']
fighter_2 = fight_list['fight_loser']
f1_team = fight_list['winner_team']
f2_team = fight_list['loser_team']
f1_division = fight_list['winner_div']
f2_division = fight_list['loser_div']
f1_conference = fight_list['winner_conf']
f2_conference = fight_list['loser_conf']
fight_relationship = fight_list['Fight Type']
winning_percent = fight_list['winning_percent']
rating = fight_list['rating']
votes = fight_list['votes']
season = fight_list['season']
ego_player_id = (((fight_list['winner'].astype(str) + "|" + fight_list['winner_team'].astype(str) + "|" + fight_list['season'].astype(str))).str.upper()).rename('ego_player_id')
alter_player_id = (((fight_list['fight_loser'].astype(str) + "|" + fight_list['loser_team'].astype(str) + "|" + fight_list['season'].astype(str))).str.upper()).rename('alter_player_id')
edge_traits = pd.concat([fighter_1,fighter_2,f1_team,f2_team,f1_division,f2_division,f1_conference,f2_conference, fight_relationship, winning_percent, rating, votes, season, ego_player_id, alter_player_id],axis=1)
edge_traits
edge_traits = edge_traits.rename(columns={"winner":"ego_name", 
                                      "fight_loser":"alter_name",
                                      "winner_team":"ego_team",
                                      "loser_team":"alter_team",
                                      "winner_div":"ego_division",
                                      "loser_div":"alter_division",
                                      "winner_conf":"ego_conference",
                                      "loser_conf":"alter_conference",
                                      "Fight Type":"fight_relationship"
                                      })
edge_traits

#Export Check
test4 = edge_traits
pd.DataFrame.to_csv(test4,r'C:\Users\chris\OneDrive\Desktop\Notre Dame\Spring 2026 - Mod 3\Networks Theory and Analysis\test4.csv')

#Import our Full Rosters and Create the player_id Column to Match node_list_2  player_abbrev, season, team
roster_import = pd.read_csv(r'C:\Users\chris\OneDrive\Desktop\Notre Dame\Spring 2026 - Mod 3\Networks Theory and Analysis\roster_list.csv', encoding="utf-8", encoding_errors='ignore')
roster_import['player'] = roster_import['player'].str.replace(r'(\(.*\))','',regex=True)
roster_import['player'] = roster_import['player'].str.replace(r'\s+$','',regex=True)
roster_import['team'] = roster_import['team'].str.replace(r'(VEG)','VGK',regex=True)
roster_import['team'] = roster_import['team'].str.replace(r'(PHX)','ARI',regex=True)
roster_import['team'] = roster_import['team'].str.replace(r'(MDA)','ANA',regex=True)
roster_import['handendness'] = roster_import['handendness'].str.replace(r'(\W+)','',regex=True)
roster_import['player_abbrev'] = roster_import['player'].str.replace(r'(^.)(\w+)','\\1.\\2',regex=True)
roster_import['player_abbrev'] = roster_import['player_abbrev'].str.replace(r'(?<=\.)(\w\.|\w+-\w+\s|\w+\s)','',regex=True)
roster_import['player_abbrev'] = roster_import['player_abbrev'].str.replace(r'\s','',regex=True)
roster_import['node_player_id'] = ((roster_import['player'].astype(str) + "|" + roster_import['birthdate'].astype(str) + "|" + roster_import['birthplace'].astype(str))).str.upper()
roster_import['edge_player_id'] = ((roster_import['player_abbrev'].astype(str) + "|" + roster_import['team'].astype(str) + "|" + roster_import['season'].astype(str))).str.upper()
roster_import = roster_import[roster_import['node_player_id'] != "PLAYER|BIRTH DATE|BIRTH"]
roster_import['node_player_id'].value_counts(dropna=False).head(20)
test_2 = roster_import
pd.DataFrame.to_csv(test_2,r'test_2.csv')

#Bring in player_id to the edge_traits DataFrame based on player_abbrev, season, team
merge1 = pd.merge(edge_traits,roster_import,left_on = ['ego_player_id'], right_on = ['edge_player_id'], how='left')
merge1
merge1 = merge1.drop(columns=['Unnamed: 0','season_y','team','player','birthdate', 'birthplace','position','age','height','weight','handendness','summary','player_abbrev'])
pd.DataFrame.to_csv(merge1,r'C:\Users\chris\OneDrive\Desktop\Notre Dame\Spring 2026 - Mod 3\Networks Theory and Analysis\merge1.csv')
merge2 = pd.merge(merge1, roster_import, left_on = ['alter_player_id'], right_on = ['edge_player_id'], how = 'left')
merge2 = merge2.drop(columns=['edge_player_id_x', 'Unnamed: 0','team','player','birthdate', 'birthdate', 'birthplace','position','age','height','weight','handendness', 'summary','player_abbrev','edge_player_id_y'])
merge2
merge2 = merge2.rename(columns={"season_x":"missing_season",
                          "node_player_id_x":"ego_node_player_id",
                          "node_player_id_y": "alter_node_player_id"
                          })
pd.DataFrame.to_csv(merge2,r'C:\Users\chris\OneDrive\Desktop\Notre Dame\Spring 2026 - Mod 3\Networks Theory and Analysis\merge2.csv')

#Import node_list to Merge On
node_list = pd.read_csv(r'C:\Users\chris\OneDrive\Desktop\Notre Dame\Spring 2026 - Mod 3\Networks Theory and Analysis\node_list_2.csv')
node_list['player_id'] = node_list['player_id'].str.upper()
node_list
merge3 = pd.merge(merge2,node_list,left_on = ['ego_node_player_id'], right_on = ['player_id'], how = 'left')
merge3
pd.DataFrame.to_csv(merge3,r'C:\Users\chris\OneDrive\Desktop\Notre Dame\Spring 2026 - Mod 3\Networks Theory and Analysis\merge3.csv')
el1 = merge3.drop(['team','player', 'Unnamed: 0', 'birthplace','birthdate','position','age','height','weight','handendness','summary','player_abbrev','player_id'], axis=1)
el1

merge4 = pd.merge(el1,node_list,left_on = ['alter_node_player_id'], right_on = ['player_id'], how = 'left')
pd.DataFrame.to_csv(merge4,r'C:\Users\chris\OneDrive\Desktop\Notre Dame\Spring 2026 - Mod 3\Networks Theory and Analysis\merge4.csv')
el2 = merge4.drop(columns=['Unnamed: 0', 'season_x','season_y','team','player','birthplace','birthdate','position','age','height','weight','handendness','summary','player_abbrev','player_id'])
el2
pd.DataFrame.to_csv(el2,r'C:\Users\chris\OneDrive\Desktop\Notre Dame\Spring 2026 - Mod 3\Networks Theory and Analysis\el2.csv')
el3 = el2.rename(columns={"ego_id_x":"ego_id",
                          "ego_id_y":"alter_id",
                          })
el3
edge_list = el3.iloc[:,[17,18,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,19]]
edge_list


#THIS INFORMATION WAS BEING USED TO HELP ME TROUBLE SHOOT THE MISSING PLAYERS IN THE DATASET
merge2['ego_node_player_id'].isna().mean()
merge2['alter_node_player_id'].isna().mean()

#Approximately 5.6% of Egos and 6.3% of Alters Failed to Load - WHY - I WAS ABLE TO DROP IT TWO 4.6% AND 5.28% - I WAS ABLE TO DROP IT TO 2.8% and 4.0%
no_match = merge2[merge2['ego_node_player_id'].isna()][
    ['ego_name','ego_team','season']
    ]

pd.DataFrame.to_csv(no_match,r'C:\Users\chris\OneDrive\Desktop\Notre Dame\Spring 2026 - Mod 3\Networks Theory and Analysis\nomatch.csv')


#Save Our Completed edge_list
pd.DataFrame.to_csv(edge_list,r'C:\Users\chris\OneDrive\Desktop\Notre Dame\Spring 2026 - Mod 3\Networks Theory and Analysis\fighters_edge_list.csv')
pd.read_csv(r'C:\Users\chris\OneDrive\Desktop\Notre Dame\Spring 2026 - Mod 3\Networks Theory and Analysis\fighters_edge_list.csv')
