#Import Required Packages
import re
import requests
import pandas as pd
import time
import json
import random
import numpy as np
from datetime import date
import seaborn as sns
import matplotlib.pyplot as plt
import os
import statsmodels.formula.api as smf

#Read in the Scraped Data

os.getcwd()
game_log = pd.read_csv(r'C:/Users/crovero/Downloads/game_information_23to25_cleaned_combo.csv')


#Seperate Date, Team Names, Final Score, Shot Count
game_log['Date'] = game_log['Meta Info'].str.replace(r'(?<=)\s.*','',regex=True)
game_log['Shots'] = game_log["Team Stats"].str.extract(r'(?=)[Team Stats](\d{4})')
game_log['Teams_Score'] = game_log['BoxScore'].str.extract(r'123(?:T|OTT|SOT)(.*)')
game_log['Team_1_Shots_For'] = game_log['Shots'].str.extract(r'^(\d{2})')
game_log['Team_2_Shots_For'] = game_log['Shots'].str.extract(r'(\d{2})$')
game_log['Team_1_Shots_For'] = pd.to_numeric(game_log['Team_1_Shots_For'])
game_log['Team_2_Shots_For'] = pd.to_numeric(game_log['Team_2_Shots_For'])
game_log['Hits'] = game_log['Team Stats'].str.extract(r'(?<=Hits)(\d{4})')
game_log['Team_1_Hits_For'] = game_log['Hits'].str.extract(r'^(\d{2})')
game_log['Team_2_Hits_For'] = game_log['Hits'].str.extract(r'(\d{2})$')
game_log['Team_1_Hits_For'] = pd.to_numeric(game_log['Team_1_Hits_For'])
game_log['Team_2_Hits_For'] = pd.to_numeric(game_log['Team_2_Hits_For'])
game_log['Total_Hits'] = game_log['Team_1_Hits_For'] + game_log['Team_2_Hits_For']
game_log['Total_Shots'] = game_log['Team_1_Shots_For'] + game_log['Team_2_Shots_For']

#Team Names
game_log['Team_1'] = game_log['Teams_Score'].str.extract(r'([A-Z]{2,3})')
game_log['Team_2_MidStep'] = game_log['Teams_Score'].str.extract(r'(?=\d+)(.*)')
game_log['Team_2'] = game_log['Team_2_MidStep'].str.extract(r'([A-Z]{2,3})')

#Final Scores
game_log['Team_2_Final_Score'] = game_log['Team_2_MidStep'].str.extract(r'(\d)$')
game_log['Team_1_Final_Score'] = game_log['Team_2_MidStep'].str.extract(r'(?=\d[A-Z])(\d)')


#Need to Create a Game Winner Column
game_log_df = pd.DataFrame(game_log)
game_log_df

gamewinners = []
for index, row in game_log_df.iterrows():
    if row['Team_1_Final_Score'] > row['Team_2_Final_Score']:
        game_winner = row['Team_1']
    else:
        game_winner = row['Team_2']

    gamewinners.append(game_winner)

game_log_df['Game_Winners'] = gamewinners

#Need to Create a Seasons Column to Match with Fightlist 
game_log_df['Date'] = pd.to_datetime(game_log_df['Date'])

s22_start = pd.Timestamp(2021,10,12)
s22_end = pd.Timestamp(2022,4,29)
s23_start = pd.Timestamp(2022,10,7)
s23_end = pd.Timestamp(2023,4,14)
s24_start = pd.Timestamp(2023,10,10)
s24_end = pd.Timestamp(2024,4,18)
s25_start = pd.Timestamp(2024,10,4)
s25_end = pd.Timestamp(2025,4,17)

seasons = []
for index, row in game_log_df.iterrows():
    if s22_start <= row['Date'] <= s22_end:
        season = '2022'
    elif s23_start <= row['Date'] <= s23_end:
        season = '2023'
    elif s24_start <= row['Date'] <= s24_end:
        season = '2024'
    else:
        season = '2025'

    seasons.append(season)
game_log_df['Season'] = seasons
game_log_df


gamew_by_season = game_log_df.groupby(['Game_Winners','Season']).size()
gamew_by_season


#Bring in the Fightlist to Combine With and Drop Irrelevant Years
fight_list = pd.read_csv(r'C:/Users/crovero/Downloads/fighters_edge_list (1).csv')
fight_list['missing_season'] = fight_list['missing_season'].astype(str)

modernlist = fight_list[fight_list['missing_season'].isin(['2022','2023','2024','2025'])]
modernlist

#Group the Fight Winners by Season
winners_by_season = modernlist.groupby(['ego_team','missing_season']).size()
winners_by_season = pd.DataFrame(winners_by_season)
winners_by_season = winners_by_season.rename(columns={0:"Fight_Wins"})

winners_by_season

#Group the Total Amount of Fights by Season
fights_by_season = pd.melt(modernlist,id_vars=["missing_season"],value_vars=["ego_team","alter_team"])
fights_by_season =  fights_by_season.groupby(['value','missing_season']).size()
fights_by_season = pd.DataFrame(fights_by_season)
fights_by_season = fights_by_season.rename(columns={0:"Total_Fights"})
fights_by_season

#Plot the Total Wins by Season and Color by Team
winners_plot = winners_by_season.reset_index()
winners_plot["missing_season"] =winners_plot["missing_season"].astype(int)
winners_plot["Fight_Wins"] = winners_plot["Fight_Wins"].astype(int)
winners_plot


gamew_plot = gamew_by_season.reset_index()
gamew_plot["Season"] = gamew_plot["Season"].astype(int)
gamew_plot = gamew_plot.rename(columns={0:"Game_Wins"})
gamew_plot['Game_Winners'] = gamew_plot['Game_Winners'].str.replace(r'(NJ)','NJD',regex=True)
gamew_plot['Game_Winners'] = gamew_plot['Game_Winners'].str.replace(r'(LA)','LAK',regex=True)
gamew_plot['Game_Winners'] = gamew_plot['Game_Winners'].str.replace(r'(SJ)','SJS',regex=True)
gamew_plot['Game_Winners'] = gamew_plot['Game_Winners'].str.replace(r'(TB)','TBL',regex=True)
gamew_plot['Game_Winners'] = gamew_plot['Game_Winners'].str.replace(r'(FLAK)','FLA',regex=True)
gamew_plot

merge = gamew_plot.merge(winners_plot, left_on = ["Game_Winners","Season"],right_on = ["ego_team","missing_season"], how="left")
merge

#Get the Total Fights by Season
total_plot = fights_by_season.reset_index()
total_plot["missing_season"] = total_plot["missing_season"].astype(int)
total_plot["Total_Fights"] = total_plot["Total_Fights"].astype(int)
total_plot

#Compare Hits to Season Fight Totals
season_hits = (
    game_log_df
    .groupby('Season')['Total_Hits']
    .sum()
    .reset_index())

season_fights = (total_plot
    .groupby('missing_season',as_index=False)['Total_Fights']
    .sum()
    .reset_index()
)
season_fights
season_hits['Season'] = season_hits['Season'].astype(int)
season_fights['Season'] = season_fights['missing_season'].astype(int)

season_compare = season_hits.merge(season_fights, left_on=['Season'],right_on=['Season'], how = 'left')
season_compare = season_compare[season_compare['Season'].isin([2023,2024,2025])]
game_log_df

team1 = game_log_df[['Team_1','Season','Team_1_Hits_For']]
team2 = game_log_df[['Team_2','Season','Team_2_Hits_For']]
team1 = team1.rename(columns={'Team_1': 'Team', 'Team_1_Hits_For': 'Hits'})
team2 = team2.rename(columns={'Team_2': 'Team', 'Team_2_Hits_For': 'Hits'})
team_games = pd.concat([team1,team2],ignore_index=True)
team_games['Hits'].isna().sum()
team_games = team_games.dropna()

team_hits = (team_games
    .groupby(['Team','Season'], as_index=False)['Hits']
    .sum()
)

team_hits
#Create Plot of Fights and Total Hits

plt.figure(figsize=(10,12))
sns.set_theme(style="whitegrid")
linear_plot = sns.lmplot(
  data = season_compare,
  x="Total_Hits", y="Total_Fights", hue="Season",
    markers=["o","s","^"],
    palette="Set2")
    
linear_plot.set_axis_labels("League Wide Total Hits","League Wide Total Fights")
linear_plot.fig.suptitle("Relationship Between Total Hits and Fights League Wide")
plt.show()

#Create a Plot of Hits vs Fights 
total_plot['missing_season'] = total_plot['missing_season'].astype(int)
team_hits['Season'] = team_hits['Season'].astype(int)
team_comparison = team_hits.merge(total_plot,left_on=["Team",'Season'],right_on=['value','missing_season'],how='left')
team_comparison = team_comparison[team_comparison['Season'].isin([2023,2024,2025])]
team_comparison_clean = team_comparison.dropna()
team_comparison_clean

plt.figure(figsize=(10,12))
sns.set_theme(style="whitegrid")
hit_labels = sns.lmplot(
    data=team_comparison_clean,
    x='Total_Fights',
    y='Hits', hue='Season',
    markers=["o","s","^"],
    palette="Set2")
hit_labels.set_axis_labels("Total Team Fights per Season","Total Team Hits For and Against")
hit_labels.fig.suptitle("Relationship Between Total Team Fights and Total Hits")

plt.show()

#Mixed Effects Model Between Hits and Total Fights

model_hits1 = smf.mixedlm(
    "Hits ~ Total_Fights",
    data=team_comparison_clean,
    groups=team_comparison_clean['Team']
).fit()

print(model_hits1.summary())

#Create a Mixed Effects Model Between Wins and Total Fights, Controlling for Season
model_hits2 = smf.mixedlm(
    "Hits ~ Total_Fights + C(Season)",
    data=team_comparison_clean,
    groups=team_comparison_clean["Team"]
).fit()

print(model_hits2.summary())

#Create a Lagged Effects Model Between Hits and Total Fights from Last Year
comparison_sorted = team_comparison_clean.sort_values(['Team','Season'])
comparison_sorted['Lagged_Fights'] = (comparison_sorted.groupby('Team')["Total_Fights"].shift(1))
comparison_sorted
comparison_sorted = comparison_sorted.dropna()

model_hits_lagged = smf.mixedlm(
    "Hits ~ Lagged_Fights + C(Season)",
    data=comparison_sorted,
    groups=comparison_sorted["Team"]
).fit()

print(model_hits_lagged.summary())

#Create Regression Plot of Fights vs Game Wins
merge2 = gamew_plot.merge(total_plot, left_on = ["Game_Winners","Season"],right_on = ["value","missing_season"], how="left")
merge2
merge2_modern = merge2[merge2['Season'].isin([2023,2024,2025])]

playoff_win_check = []

for index,row in merge2_modern.iterrows():
  if row['Game_Wins'] >= 42:
    playoff_wins = "Yes"
  else:
    playoff_wins = "No"
  playoff_win_check.append(playoff_wins)
merge2_modern['playoff_wins'] = playoff_win_check
merge2_modern

plt.figure(figsize=(10,12))
sns.set_theme(style="whitegrid")
linear_plot = sns.lmplot(
  data = merge2_modern,
  x="Total_Fights", y="Game_Wins", hue="Season",
    markers=["o","s","^"],
    palette="Set2")
    
linear_plot.set_axis_labels("Total Team Fights per Season","Team Regular Season Wins")
linear_plot.fig.suptitle("Relationship Between Total Team Fights and Regular Season Wins")
plt.show()


#Create a Plot of Number of Fights Per Team for Each Season

#2023 Season
Season_2023 = merge2_modern[merge2_modern['Season'].isin([2023])]
Season_2023 = Season_2023.sort_values('Total_Fights')
Season_2023

plt.figure(figsize=(10,12))
g = sns.catplot(
    data=Season_2023, kind="bar",
    x="value", y="Total_Fights", hue="playoff_wins",
    palette="dark", alpha=.6, height=6
)
g.despine(left=True)
g.set_axis_labels("", "Total Team Fights")
g.fig.suptitle("Most Prolific Fighting Teams of 2023 Season")
plt.xticks(rotation=45)
g._legend.set_title("42+ Wins")
plt.show()

#2024 Season
Season_2024 = merge2_modern[merge2_modern['Season'].isin([2024])]
Season_2024 = Season_2024.sort_values('Total_Fights')
Season_2024

plt.figure(figsize=(10,12))
g = sns.catplot(
    data=Season_2024, kind="bar",
    x="value", y="Total_Fights", hue="playoff_wins",
    palette="dark", alpha=.6, height=6
)
g.despine(left=True)
g.set_axis_labels("", "Total Team Fights")
g.fig.suptitle("Most Prolific Fighting Teams of 2024 Season")
plt.xticks(rotation=45)
g._legend.set_title("42+ Wins")
plt.show()

#2025 Season
Season_2025 = merge2_modern[merge2_modern['Season'].isin([2025])]
Season_2025 = Season_2025.sort_values('Total_Fights')
Season_2025

plt.figure(figsize=(10,12))
g = sns.catplot(
    data=Season_2025, kind="bar",
    x="value", y="Total_Fights", hue="playoff_wins",
    palette="dark", alpha=.6, height=6
)
g.despine(left=True)
g.set_axis_labels("", "Total Team Fights")
g.fig.suptitle("Most Prolific Fighting Teams of 2025 Season")
plt.xticks(rotation=45)
g._legend.set_title("42+ Wins")
plt.show()


#Check for and Drop NAs (Should be 1 for Arizona)
merge2_modern.isna().sum()
merge2_modern = merge2_modern.dropna()
merge2_modern
total_fights = merge2_modern.groupby('value')['Total_Fights'].sum()
total_fights = total_fights.reset_index()
total_wins = merge2_modern.groupby('value')['Game_Wins'].sum()
total_wins = total_wins.reset_index()
totals = total_fights.merge(total_wins, on = ["value"], how = "left")
totals = totals.sort_values('Total_Fights')
wins_mean = totals['Game_Wins'].mean()

wins_avg = []

for index, row in totals.iterrows():
  if row['Game_Wins'] >= 126:
    wins_check = "Yes"
  else:
    wins_check = "No"
  wins_avg.append(wins_check)
totals['wins_avg_check'] = wins_avg
totals

plt.figure(figsize=(10,12))
g = sns.catplot(
    data=totals, kind="bar",
    x="value", y="Total_Fights", hue="wins_avg_check",
    palette="dark", alpha=.6, height=6
)
g.despine(left=True)
g.set_axis_labels("", "Total Team Fights")
g.fig.suptitle("Most Prolific Fighting Teams of the 2023 through 2025 Seasons")
plt.xticks(rotation=45)
g._legend.set_title("126+ Wins")
plt.show()

pd.DataFrame.to_csv(merge2_modern,r'C:/Users/crovero/Downloads/merge2.csv')


#Create a Mixed Effects Model Between Wins and Total Fights
model_mixed = smf.mixedlm(
    "Game_Wins ~ Total_Fights",
    data=merge2_modern,
    groups=merge2_modern["value"]
).fit()

print(model_mixed.summary())

#Create a Mixed Effects Model Between Wins and Total Fights, Controlling for Season
model_mixed_2 = smf.mixedlm(
    "Game_Wins ~ Total_Fights + C(Season)",
    data=merge2_modern,
    groups=merge2_modern["value"]
).fit()

print(model_mixed_2.summary())

#Create a Lagged Effects Model Between Wins and Total Fights from Last Year
merge2_sorted = merge2_modern.sort_values(['value','Season'])
merge2_sorted['Lagged_Fights'] = (merge2_sorted.groupby('value')["Total_Fights"].shift(1))
merge2_sorted = merge2_sorted.dropna()

model_lagged = smf.mixedlm(
    "Game_Wins ~ Lagged_Fights + C(Season)",
    data=merge2_sorted,
    groups=merge2_sorted["value"]
).fit()

print(model_lagged.summary())
