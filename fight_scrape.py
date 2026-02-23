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