# coding: utf-8

# In[12]:

import numpy as np
import pandas as pd
from dateutil.relativedelta import relativedelta
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait


class AcquireNFLGameStats(object):
    def __init__(self, year1, year2):
        self.year1 = year1
        self.year2 = year2

    def __call__(self):
        print "Scraping game data..."
        self.get_nfl_game_stats_column_headers(self.year1)
        self.get_nfl_game_stats(self.year1, self.year2, self.column_headers)
        self.clean_nfl_game_data(self.game_df)
        print "Scraping game data...OK"

    def get_nfl_game_stats_column_headers(self, year1):

        url = "http://www.pro-football-reference.com/years/{year1}/games.htm"
        url = url.format(year1=year1)
        browser = webdriver.Chrome("C:\Users\jbadiabo\PycharmProjects\Sibyl\chromedriver.exe")

        delay = 5  # seconds

        while True:
            try:
                browser.set_page_load_timeout(20)
                while True:
                    try:
                        browser.get(url)
                    except TimeoutException:
                        print "Timeout, retrying..."
                        continue
                    else:
                        break
                WebDriverWait(browser, delay).until(ec.presence_of_element_located((By.ID, "games")))
            except TimeoutException:
                browser.quit()
                delay += 3
                continue
            break

        table = browser.find_element_by_id('games')
        head = table.find_element_by_tag_name('thead')

        head_line = head.find_element_by_tag_name('tr')

        column_headers = [header.text.encode('utf8') for header in head_line.find_elements_by_tag_name('th')]

        self.column_headers = column_headers[1:]

        browser.quit()

    def get_nfl_game_stats(self, year1, year2, column_headers):

        url_template = "http://www.pro-football-reference.com/years/{year}/games.htm"
        game_df = pd.DataFrame()

        for year in range(year1, year2 + 1):
            file_data = []
            url = url_template.format(year=year)
            browser = webdriver.Chrome("C:\Users\jbadiabo\PycharmProjects\Sibyl\chromedriver.exe")

            delay = 5  # seconds

            while True:
                try:
                    browser.set_page_load_timeout(20)
                    while True:
                        try:
                            browser.get(url)
                        except TimeoutException:
                            print "Timeout, retrying..."
                            continue
                        else:
                            break
                    WebDriverWait(browser, delay).until(ec.presence_of_element_located((By.ID, "games")))
                except TimeoutException:
                    browser.quit()
                    delay += 3
                    continue
                break

            table = browser.find_element_by_id('games')
            body = table.find_element_by_tag_name('tbody')

            body_rows = body.find_elements_by_tag_name('tr')

            for row in body_rows:
                data = row.find_elements_by_tag_name('td')
                file_row = [datum.text.encode('utf8') for datum in data]

                file_data.append(file_row)

            year_df = pd.DataFrame(file_data, columns=column_headers)
            year_df.insert(0, 'Season_Yr', year)

            game_df = game_df.append(year_df, ignore_index=True)

            browser.quit()

        self.game_df = game_df

    def clean_nfl_game_data(self, game_df):

        # drop the Time column for the 2016 season 
        try:
            game_df.drop('Time', axis=1, inplace=True)
        except:
            pass

        game_df = game_df[(game_df['Winner/tie'].notnull())]
        game_df = game_df[(game_df['Winner/tie'] != "")]

        game_df.rename(columns={'': 'Away_or_not'}, inplace=True)

        # Rename duplicates so as to drop the last one from the df 

        cols = pd.Series(game_df.columns)

        for dup in game_df.columns.get_duplicates():
            cols[game_df.columns.get_loc(dup)] = ['D_' + dup if d_idx != 0 else dup for d_idx in
                                                  range(game_df.columns.get_loc(dup).sum())]

        game_df.columns = cols

        cols = [c for c in game_df.columns if c.lower()[:2] != 'd_']
        game_df = game_df[cols]

        cols = [c for c in game_df.columns if c.lower()[:2] != 'd_']
        game_df = game_df[cols]

        game_df.drop(game_df.columns[[8, 9, 10, 11]], axis=1, inplace=True)

        self.game_df = game_df

        # Fill the blank for the 2016 season
        game_df['PtsL'] = game_df['PtsL'].replace(r'\s+( +\.)|#', np.nan, regex=True).replace('', np.nan)
        game_df['PtsW'] = game_df['PtsW'].replace(r'\s+( +\.)|#', np.nan, regex=True).replace('', np.nan)
        game_df = game_df[game_df.Day.notnull()]
        game_df['PtsL'].fillna(0, inplace=True)
        game_df['PtsW'].fillna(1, inplace=True)

        game_df['Visitor_Team'] = ''
        game_df['Visitor_Team_PTS'] = ''
        game_df['Home_Team'] = ''
        game_df['Home_Team_PTS'] = ''

        Visitor_Team = []
        Home_Team = []

        Visitor_Team_PTS = []
        Home_Team_PTS = []

        for row, winner, loser, winner_pts, loser_pts in zip(game_df['Away_or_not'], game_df['Winner/tie'],
                                                             game_df['Loser/tie'], game_df['PtsW'], game_df['PtsL']):
            if row in ('', 'N'):
                Visitor_Team.append(loser)
                Home_Team.append(winner)
                Visitor_Team_PTS.append(loser_pts)
                Home_Team_PTS.append(winner_pts)
            else:
                Visitor_Team.append(winner)
                Home_Team.append(loser)
                Visitor_Team_PTS.append(winner_pts)
                Home_Team_PTS.append(loser_pts)

        game_df['Visitor_Team'] = Visitor_Team
        game_df['Visitor_Team_PTS'] = Visitor_Team_PTS
        game_df['Home_Team'] = Home_Team
        game_df['Home_Team_PTS'] = Home_Team_PTS

        game_df = game_df.drop(game_df[[1, 3, 4, 5, 6, 7]], axis=1)

        game_df['Date'] = game_df['Date'].str.strip().str.replace(' ', ',')

        game_df['Date'] = game_df['Season_Yr'].map(str) + ',' + game_df['Date']

        game_df['Date'] = pd.to_datetime(game_df['Date'], infer_datetime_format=True)
        game_df['Date'] = game_df['Date'].apply(lambda x: x + relativedelta(years=1) if 1 <= x.month <= 6 else x)

        game_df['Visitor_Team_PTS'] = pd.to_numeric(game_df['Visitor_Team_PTS'])
        game_df['Home_Team_PTS'] = pd.to_numeric(game_df['Home_Team_PTS'])
        game_df['Season_Yr'] = game_df['Season_Yr'].astype(str)

        # Extracting exclusively the 'Date' column to a csv file
        # for further analysis in Tableau with "tableau_input" file
        game_df['Date'].to_csv("date_nfl_game_stats_" + str(self.year1) + "_" + str(self.year2) + ".csv", mode='w+',
                               header=False, index=False)

        # Dropping the column 'Date' as we do not need it anymore
        game_df.drop('Date', axis=1, inplace=True)

        game_df.to_csv("nfl_game_stats_" + str(self.year1) + "_" + str(self.year2) + ".csv", index=False, mode='w+')
