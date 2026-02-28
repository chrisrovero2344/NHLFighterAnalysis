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
import time
from datetime import datetime, timedelta

#First We Need to Create a List of Games We Want to Study

#start_date = datetime(2022, 2, 1)
start_date = datetime(2021, 10, 10)
end_date = datetime(2026, 1, 25)
date_str = start_date.strftime("%Y%m%d")
headers = {'User-Agent':'Mozilla 5.0'}

game_link_list = []

for i in range(0, (end_date - start_date).days + 1, 7):
    d = start_date + timedelta(days=i)
    date_str = d.strftime("%Y%m%d")
    hockey_games_link = f"https://www.espn.com/nhl/schedule/_/date/{date_str}"

    games_link_request = requests.get(hockey_games_link, headers=headers)

    games_link_request

    weekly_content = games_link_request.text

    weekly_soup = BeautifulSoup(weekly_content)

    game_links_extract = weekly_soup.select("a[href*=gameId]")

    game_linkers = [game.get('href') for game in game_links_extract]

    link_output = pd.DataFrame(game_linkers)

    game_link_list.append(link_output)

game_link_list_df = pd.concat(game_link_list)
game_link_list_df

pd.DataFrame.to_csv(game_link_list_df,r'Downloads/game_links.csv')


#We Need to Playwright The Individual Game Pages for Game Summary Information - Open the ESPN Page and Navigate to Each Game Page 
pw = sync_playwright().start()

chrome = pw.chromium.launch(headless=False)

page = chrome.new_page()

game_information = []

game_link_list_2 = game_link_list_df[0].tolist()
game_link_list_df
game_link_list_2
for game in game_link_list_2:
    page.goto(f'https://www.espn.com{game}', wait_until='domcontentloaded')
    if "404" in page.title().lower():
        continue
    time.sleep(0.2)
    game_content = page.content()

    game_soup = BeautifulSoup(game_content)
    game_soup

    if 'Postponed' in game_content:
        continue

    allstar_check = game_soup.select('.mLASH')
    allstar_check = [x.text.strip() for x in allstar_check]
    if 'NHL All-Star - Semifinal' in allstar_check:
        continue

    if 'NHL All-Star - Final' in allstar_check:
        continue

    if '4 Nations Face-Off - Championship' in allstar_check:
        continue

    meta_info = game_soup.select('.n8')
    meta_info = [x.text.strip() for x in meta_info[0]]
    meta_info = meta_info[0]

    scorebox = game_soup.select('.zdu')
    scorebox = [x.text.strip() for x in scorebox]
    scorebox

    team_stats = game_soup.select('.liAe')
    team_stats = [x.text.strip() for x in team_stats]
    team_stats

    first_scoring_summary = game_soup.select('table')
    first_scoring_summary = [x.text.strip() for x in first_scoring_summary]
    first_scoring_summary = "|".join(first_scoring_summary)
    
    second_scoring_summary = game_soup.select('table')
    second_scoring_summary = [x.text.strip() for x in second_scoring_summary[3]]
    second_scoring_summary = "|".join(second_scoring_summary)

    third_scoring_summary = game_soup.select('table')
    third_scoring_summary = [x.text.strip() for x in third_scoring_summary[4]]
    third_scoring_summary = "|".join(third_scoring_summary)
    
    page.locator('css=button', has_text='Penalties').click()

    penalty_content = page.content()
    penalty_soup = BeautifulSoup(penalty_content)
    penalty_soup

    first_penalty_summary = penalty_soup.select('table')
    first_penalty_summary = [x.text.strip() for x in first_penalty_summary[2]]
    first_penalty_summary = "|".join(first_penalty_summary)
    
    second_penalty_summary = penalty_soup.select('table')
    second_penalty_summary = [x.text.strip() for x in second_penalty_summary[3]]
    second_penalty_summary = "|".join(second_penalty_summary)
    
    third_penalty_summary = penalty_soup.select('table')
    third_penalty_summary = [x.text.strip() for x in third_penalty_summary[4]]
    third_penalty_summary = "|".join(third_penalty_summary)

    output = pd.DataFrame({
        "Meta Info": meta_info,
        "BoxScore": scorebox,
        "Team Stats": team_stats,
        "First Scoring Summary": first_scoring_summary,
        "Second Scoring Summary": second_scoring_summary,
        "Third Scoring Summary": third_scoring_summary,
        "First Penalty Summary": first_penalty_summary,
        "Second Penalty Summary": second_penalty_summary,
        "Third Penalty Summary": third_penalty_summary},
        index=[0]
    ) 
    
    game_information.append(output)

game_information_df = pd.concat(game_information)
game_information_df

pd.DataFrame.to_csv(game_information_df,r'Downloads/game_information.csv')