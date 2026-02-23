# NHL Fighter Analysis


## In-Depth Anyalysis of the Threat of Moderated Combatants and Injury Deterrence in the Modern NHL

### Background and Role of Fighting in the NHL

Five years into the National Hockey League, in 1922 Rule 56 was
officially instituted in the NHL rulebook. Fisticuffs, condones the act
of fighting between two individuals stating that the two players will be
assessed a five minute major penalty, along with some other language
about instigation which has since largely been abandonded. By modern
definition, a fight is defined as when at least one player punches or
attempts to punch an opponent repeatedly or two players wrestle in such
a manner that make it difficult for officials to intervene. Since its
inception, the the presence of fighting has been grounded in its ability
to deter violent, injury-prone behavior throughout gameplay, with the
notion that self-regulation and threat of having to respond to an
altercation will detract players from engaging in dangerous play.

Annectodally, over the past decade, the appearance of altercations in
relation to play related to intent to injury or illegal collisions has
been seemingly dwarfed by those altercations ignited by violent legal
collisions, emotional factors such as game outcome, or simply
premeditated. The latter of which directly contradict the NHL’s original
intent of the activity, and has been a subject of fan’s sore attitude
for years. In an attempt to further understand the role, importance, and
necessity of fighting in the NHL, this research aims to analyze the
networks effects of players engaged in bouts of belligerence and predict
the sucess of NHL teams and franchises based on engagement in the
activity.

To begin the investigation, top-level descriptive network analysis was
conducted. First, fighting prevalence by count of altercations per
season was plotted as shown below. Annual altercations since the 2000
season certainly have been on the decline up until modern day, which is
consistent with the theory that the the threat of fighting is effective
as deterring injure-prone behavior. However, alternative reasonings
could be suggested as the core cause of the decline, such as skill-gap
closure, demographic shifts, or cultural shifts within the league and is
not conclusive evidence of deterrence.

![AnnualAltercationCount](Data/AnnualAltercationCount.png)

## Features

The NHL Fighter Analysis program is designed as a free tool for NHL
organizations, analysts, and fans to track and analyze player
altercations in the National Hockey League. This application extracts
all NHL roster information from hockey-reference.com and all recorded
Fighting Majors from hockeyfights.com for seasons of interest (set to
2000-2026 seasons), and utilizes Python and R packages to demonstrate
network effect and predictive modeling of player altercations to aid in
league decision making.

## Tech Stack

### Data Collection and Cleaning:

- Python, PySide6(QtWidgets), Pandas, Regex
- Web Scraping: Playwright, BeautifulSoup4, Requests

### Data Analsysis:

- Network Analysis: R (btergm)

## Data Collection and Cleaning Walkthrough

### 1) 2000-2026 NHL Rosters Scraped from hockey-reference.com

#### 1a.) Unique Player Indentification

Node List:

For establishment of a complete node list, each player is uniquely
identified under the assumption that no plyer simultaneously shares the
same Full Name, Birthdate, and Birthplace between Seasons 2000-2026.

Edge List:

For establishment and merging of the complete edge list, each player
from every roster is given a non-unique ID

### 2) 2000-2026 NHL Fighting Majors Scraped from hockeyfights.com

### 3)

### 4)

## Getting Started (Run Locally)

### 1) Clone the Repository

``` bash

git clone https://github.com/chrisrovero2344/NHLFighterAnalysis

cd ~/NHLFighterAnalysis
```

### 2) Create and Activate a Virtual Environment in the Repository (Windows PowerShell)

``` powershell

py -m venv venv

Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

.\\venv\\Scripts\\Activate.ps1
```

You should see `(venv)` in your terminal prompt.

### 3) Install Dependencies

``` powershell

pip install --upgrade pip

pip install pandas, bs4, requests, playwright
```

### 4) Run the Roster Scraping Script

``` powershell

python roster_scrape.py
```

### 5) Run the Fight Scraping Script

``` powershell

python fight_scrape.py
```

### 6) Run the Edge List Creation Script

``` powershell

python edge_list_creation.py
```

## Inspiration
