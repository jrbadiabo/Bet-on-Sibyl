# coding: utf-8

# In[1]:

# from urllib import urlopen
import numpy as np
import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait


class AcquireNHLGameStats(object):
    def __init__(self, year1, year2):
        self.year1 = year1
        self.year2 = year2

    def __call__(self):
        print "Scraping game data..."
        self.get_nhl_game_stats_column_headers(self.year1)
        self.get_nhl_game_stats(self.year1, self.year2, self.regular_column_headers)
        self.concat_dfs(self.regular_game_df, self.playoff_game_df)
        self.clean_nfl_game_data(self.game_df)
        print "Scraping game data...OK"

    def get_nhl_game_stats_column_headers(self, year1):

        browser = webdriver.Chrome("C:\Users\jbadiabo\PycharmProjects\Sibyl\chromedriver.exe")
        url_template = "http://www.hockey-reference.com/leagues/NHL_{year1}_games.html"
        url = url_template.format(year1=year1)
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

        regular_column_headers = [header.text.encode('utf8') for header in head_line.find_elements_by_tag_name('th')]
        self.regular_column_headers = regular_column_headers

        # --------------------------------------------- PLAYOFFS -----------------------------------------------------

        try:
            table = browser.find_element_by_id('games_playoffs')
            head = table.find_element_by_tag_name('thead')

            head_line = head.find_element_by_tag_name('tr')

            playoff_column_headers = [header.text.encode('utf8') for header in
                                      head_line.find_elements_by_tag_name('th')]

            self.playoff_column_headers = playoff_column_headers

        except:
            pass  # Handling this exception in the case of the current season

        browser.quit()

    def get_nhl_game_stats(self, year1, year2, regular_column_headers):

        url_template = "http://www.hockey-reference.com/leagues/NHL_{year}_games.html"
        regular_game_df = pd.DataFrame()
        playoff_game_df = pd.DataFrame()

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

                file_row = []
                for datum in data:
                    try:
                        datum = datum.text.encode('utf8')
                        file_row.append(datum)
                    except:
                        file_row.append(datum)

                head_data = row.find_element_by_tag_name('th')
                file_head = [head_data.text.encode('utf8')]
                file_head.extend(file_row)

                file_data.append(file_head)

            regular_year_df = pd.DataFrame(file_data, columns=regular_column_headers)
            regular_year_df.insert(0, 'Season_Yr', year)

            regular_game_df = regular_game_df.append(regular_year_df, ignore_index=True)

            # --------------------------------- PLAYOFF -------------------------------------------------------
            try:
                file_data = []

                table = browser.find_element_by_id('games_playoffs')
                body = table.find_element_by_tag_name('tbody')

                body_rows = body.find_elements_by_tag_name('tr')

                for row in body_rows:
                    data = row.find_elements_by_tag_name('td')

                    file_row = []
                    for datum in data:
                        try:
                            datum = datum.text.encode('utf8')
                            file_row.append(datum)
                        except:
                            file_row.append(datum)

                    head_data = row.find_element_by_tag_name('th')
                    file_head = [head_data.text.encode('utf8')]
                    file_head.extend(file_row)

                    file_data.append(file_head)

                playoff_year_df = pd.DataFrame(file_data, columns=self.playoff_column_headers)
                playoff_year_df.insert(0, 'Season_Yr', year)

                playoff_game_df = playoff_game_df.append(playoff_year_df, ignore_index=True)
            except:
                pass  # Handling this exception in the case of the current season

            browser.quit()

        self.regular_game_df = regular_game_df
        self.playoff_game_df = playoff_game_df

    def concat_dfs(self, regular_game_df, playoff_game_df):
        frames = [regular_game_df, playoff_game_df]
        game_df = pd.concat(frames)
        self.game_df = game_df

    def clean_nfl_game_data(self, game_df):
        # drop the Time column for the 2016 season 
        try:
            game_df.drop('Time', axis=1, inplace=True)
        except:
            pass

        game_df = game_df[(game_df['Date'].notnull())]
        game_df = game_df[(game_df['Date'] != "")]

        # Rename duplicates so as to drop the last one from the df 

        cols = pd.Series(game_df.columns)

        for dup in game_df.columns.get_duplicates():
            cols[game_df.columns.get_loc(dup)] = ['H_' + dup if d_idx != 0 else 'V_' + dup for d_idx in
                                                  range(game_df.columns.get_loc(dup).sum())]

        game_df.columns = cols

        game_df.drop(game_df[[6, 7, 8, 9]], axis=1, inplace=True)

        self.game_df = game_df

        # Fill the blank for the 2016 season
        game_df['V_G'] = game_df['V_G'].replace(r'\s+( +\.)|#', np.nan, regex=True).replace('', np.nan)
        game_df['H_G'] = game_df['H_G'].replace(r'\s+( +\.)|#', np.nan, regex=True).replace('', np.nan)
        game_df = game_df[game_df.Date.notnull()]
        game_df['V_G'].fillna(0, inplace=True)
        game_df['H_G'].fillna(1, inplace=True)

        game_df['Visitor_Team'] = game_df['Visitor']
        game_df['Visitor_Team_PTS'] = game_df['V_G']
        game_df['Home_Team'] = game_df['Home']
        game_df['Home_Team_PTS'] = game_df['H_G']

        game_df.drop(game_df[[2, 3, 4, 5]], axis=1, inplace=True)

        self.game_df = game_df

        game_df['Date'] = pd.to_datetime(game_df['Date'], infer_datetime_format=True)

        game_df['Visitor_Team_PTS'] = pd.to_numeric(game_df['Visitor_Team_PTS'])
        game_df['Home_Team_PTS'] = pd.to_numeric(game_df['Home_Team_PTS'])
        game_df['Season_Yr'] = game_df['Season_Yr'].astype(str)

        game_df['Visitor_Team_PTS'].fillna(0, inplace=True)
        game_df['Home_Team_PTS'].fillna(1, inplace=True)

        try:
            game_df['Home_Team_PTS'] = game_df['Home_Team_PTS'].astype(int)
            game_df['Visitor_Team_PTS'] = game_df['Visitor_Team_PTS'].astype(int)

        # Simulate some True Result for unplayed game in the current season 
        # Avoiding error when making the input_tableau file
        except (ValueError, KeyError) as e:
            game_df['Home_Team_PTS'] = game_df['Home_Team_PTS'].replace([''], 1)
            game_df['Visitor_Team_PTS'] = game_df['Visitor_Team_PTS'].replace([''], 0)
            game_df['Home_Team_PTS'] = game_df['Home_Team_PTS'].astype(int)
            game_df['Visitor_Team_PTS'] = game_df['Visitor_Team_PTS'].astype(int)

        # Extracting exclusively the 'Date' column to a csv file
        # or further analysis in Tableau with "tableau_input" file
        game_df['Date'].to_csv("date_nhl_game_stats_" + str(self.year1) + "_" + str(self.year2) + ".csv", mode='w+',
                               header=False, index=False)

        # Dropping the column 'Date' as we do not need it anymore
        game_df.drop('Date', axis=1, inplace=True)

        game_df.to_csv("nhl_game_stats_" + str(self.year1) + "_" + str(self.year2) + ".csv", index=False, mode='w+')
