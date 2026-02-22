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

#Set Variables for Years of Interest

year_list = list(range(2000,2027))


#We Had to Add Some Extra Names Here Like MDA to Account for Changes Over Time
divisions = {'Atlantic':('TBL','MTL','DET','BUF','BOS','OTT','TOR','FLA'),
    'Metropolitan':('CAR','PIT','NYI','NYR','NJD','WSH','CBJ','PHI'),
    'Central':('COL','MIN','DAL','UTA','NSH','WPG','STL','CHI'),
    'Pacific':('VEG','CGY','SEA','ANA','VAN','EDM','LAK','SJS','MDA'),
    'No Division':('ATL','ARI', 'PHX')}

#Here is the Link I will Use to Pull in Player Information, Lets Make Sure it Works, HAHAHAHA I LOVE STACKEDOVERFLOW, We Can Add This to the NodeList
teams = set().union(*divisions.values())
headers_2 = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36'}

roster_df = []

pw = sync_playwright().start()

chrome = pw.chromium.launch(headless=False)

page = chrome.new_page()

for team in teams:
    for year in year_list:
        player_info_link = f"https://www.hockey-reference.com/teams/{team}/{year}.html"
        if "2005" in player_info_link.title().lower():
            continue
        page.goto(player_info_link, wait_until='domcontentloaded')
        time.sleep(5)
        page_content = page.content()
        if "Page Not Found" in page_content:
            continue
        else:
            roster_content = pd.read_html(page_content)
        if "Injury Note" in page_content:
            roster_info = roster_content[14]
        else:
            roster_info = roster_content[13]
        
        roster_info_df = roster_info
        roster_info_df
        print(player_info_link)

        roster_output = pd.DataFrame({
            "season": year,
            "team": team,
            "player": roster_info_df['Player'],
            "birthplace": roster_info_df['Birth'],
            "birthdate": roster_info_df['Birth Date'],
            "position": roster_info_df['Pos'],
            "age": roster_info_df['Age'],
            "height": roster_info_df['Ht'],
            "weight": roster_info_df['Wt'],
            "handendness": roster_info_df['S/C'],
            "summary": roster_info_df['Summary']
            })
        
        roster_df.append(roster_output)

roster_extraction = pd.concat(roster_df)
roster_data_extract = pd.DataFrame(roster_extraction)
roster_data_extract

pd.DataFrame.to_csv(roster_data_extract,r'C:\Users\chris\OneDrive\Desktop\Notre Dame\Spring 2026 - Mod 3\Networks Theory and Analysis\roster_list.csv')

#We Need to Create a Real Nodelist
rosters = pd.read_csv(r'C:\Users\chris\OneDrive\Desktop\Notre Dame\Spring 2026 - Mod 3\Networks Theory and Analysis\roster_list.csv')
rosters

#Start By Removing Captaincy Labels and Matching Team Names to Fight List
rosters['player'] = rosters['player'].str.replace(r'(\(.*\))','',regex=True)
rosters['player'] = rosters['player'].str.replace(r'\s+$','',regex=True)
rosters['team'] = rosters['team'].str.replace(r'(VEG)','VGK',regex=True)
rosters['team'] = rosters['team'].str.replace(r'(PHX)','ARI',regex=True)
rosters['team'] = rosters['team'].str.replace(r'(MDA)','ANA',regex=True)
rosters['handendness'] = rosters['handendness'].str.replace(r'(\W+)','',regex=True)
rosters['player_abbrev'] = rosters['player'].str.replace(r'(^.)(\w+)','\\1.\\2',regex=True)
rosters['player_abbrev'] = rosters['player_abbrev'].str.replace(r'(?<=\.)(\w+\s)','',regex=True)
#rosters['points'] = rosters['summary'].str.extract(r'(\d+)\w+\s$')
rosters

#Augment the Dataset with a Concatenated ID Column and Remove Duplicates, Assumes No Player Shares Same Name, Birthdate, and Birthplace Simultanesouly
rosters['player_id'] = rosters['player'].astype(str).fillna(pd.NA)+ "|" + rosters['birthdate'].astype(str).fillna(pd.NA) + "|" + rosters['birthplace'].astype(str).fillna(pd.NA)
unique_players_final = rosters.drop_duplicates('player_id').reset_index(drop=True)
unique_players_final = unique_players_final.iloc[:,[1,2,3,4,5,6,7,8,9,10,11,12,13]]
unique_players_final

#Exported This, We Have 37 Total Players with the Same Name
unique_players_final.value_counts('player')
unique_players_final.value_counts('player_id')
pd.DataFrame.to_csv(unique_players_final,r'C:\Users\chris\OneDrive\Desktop\Notre Dame\Spring 2026 - Mod 3\Networks Theory and Analysis\unique_players.csv')

#Now We Need to Create an ID Column and Create the Nodelist
length = len(unique_players_final)
ego_id = pd.DataFrame(list(range(1, length+1)),columns=['ego_id'])
len(ego_id)
nodelist = pd.concat([ego_id,unique_players_final], axis=1)
nodelist

pd.DataFrame.to_csv(nodelist,r'C:\Users\chris\OneDrive\Desktop\Notre Dame\Spring 2026 - Mod 3\Networks Theory and Analysis\node_list_2.csv',encoding='utf-8')