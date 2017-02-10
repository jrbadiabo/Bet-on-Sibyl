# coding: utf-8

# In[53]:

import numpy as np
import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait


class AcquireNBAGameStats(object):
    def __init__(self, year1, year2):
        self.year1 = year1
        self.year2 = year2

    def __call__(self):
        print "Scraping game data..."
        self.get_nba_game_stats_column_headers(self.year1)
        self.get_nba_game_stats(self.year1, self.year2, self.column_headers)
        print "Scraping game data...OK"
        print "Data cleaning..."
        self.clean_nba_game_data(self.game_df)
        print "Data cleaning...OK"

    def get_nba_game_stats_column_headers(self, year1):

        browser = webdriver.Chrome("C:\Users\jbadiabo\PycharmProjects\Sibyl\chromedriver.exe")
        url = "http://www.basketball-reference.com/leagues/NBA_{year1}_games.html"
        url = url.format(year1=year1)

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
                WebDriverWait(browser, delay).until(ec.presence_of_element_located((By.ID, "schedule")))
            except TimeoutException:
                browser.quit()
                continue
            break

        browser.maximize_window()

        table = browser.find_element_by_id('schedule')
        head = table.find_element_by_tag_name('thead')

        head_line = head.find_element_by_tag_name('tr')

        self.column_headers = [header.text.encode('utf8') for header in head_line.find_elements_by_tag_name('th')]

        browser.quit()

    def get_nba_game_stats(self, year1, year2, column_headers):

        url_template = "http://www.basketball-reference.com/leagues/NBA_{year}_games-{month}.html"
        game_df = pd.DataFrame()

        month_xpath_template = ".//div[@class='filter']/div[{i}]/a"

        browser = webdriver.Chrome("C:\Users\jbadiabo\PycharmProjects\Sibyl\chromedriver.exe")

        months = ['october', 'november', 'december', 'january', 'february', 'march', 'april', 'may', 'june']

        delay = 5  # seconds

        for year in range(year1, year2 + 1):

            for i, month in zip(range(1, 10), months):

                url = url_template.format(year=year, month=month)

                try:
                    file_data = []

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
                            WebDriverWait(browser, delay).until(ec.presence_of_element_located((By.ID, "schedule")))
                        except TimeoutException:
                            browser.quit()
                            continue
                        break

                    browser.maximize_window()

                    table = browser.find_element_by_id('schedule')
                    body = table.find_element_by_tag_name('tbody')

                    body_rows = body.find_elements_by_tag_name('tr')

                    for row in body_rows:
                        data = row.find_elements_by_tag_name('td')
                        file_row = [datum.text.encode('utf8') for datum in data]
                        head_data = row.find_element_by_tag_name('th')
                        file_head = [head_data.text.encode('utf8')]
                        self.file_head = file_head.extend(file_row)
                        file_data.append(file_head)

                    year_df = pd.DataFrame(file_data, columns=column_headers)
                    year_df.insert(0, 'Season_Yr', year)
                    try:
                        year_df = year_df.drop('Start (ET)', axis=1)
                    except:
                        pass

                    game_df = game_df.append(year_df, ignore_index=True)

                    next_month_page = browser.find_element_by_xpath((month_xpath_template).format(i=i))

                    try:
                        next_month_page.click()
                    except:
                        browser.refresh()
                        next_month_page = browser.find_element_by_xpath((month_xpath_template).format(i=i))
                        next_month_page.click()
                except:
                    continue

            if year != 2017:
                # to iterate within each year...
                try:
                    next_page = browser.find_element_by_class_name("button2 next")
                    next_page.click()
                except WebDriverException:
                    try:
                        browser.refresh()
                        next_page = browser.find_element_by_class_name("button2 next")
                        next_page.click()
                    except:
                        continue
            else:
                pass

        self.game_df = game_df
        browser.quit()

    def clean_nba_game_data(self, game_df):

        # Infer the column values to the appropriate type
        game_df = game_df.apply(pd.to_numeric, errors='ignore')
        # Renaming some column names
        game_df.columns = game_df.columns.str.replace('Visitor/Neutral', 'Visitor_Team1')
        game_df.columns = game_df.columns.str.replace('Home/Neutral', 'Home_Team1')
        # Remove row with missing values at the 'Date' column
        game_df = game_df[game_df.Date.notnull()]
        # Renaming the duplicates to avoid some issues when uploading in sqlite
        cols = pd.Series(game_df.columns)
        for dup in game_df.columns.get_duplicates():
            cols[game_df.columns.get_loc(dup)] = ['H_' + dup if d_idx != 0 else 'V_' + dup for d_idx in
                                                  range(game_df.columns.get_loc(dup).sum())]
        game_df.columns = cols

        game_df.dropna(subset=['Date'])

        # Convert game points to integer
        game_df['Visitor_Team'] = game_df['Visitor_Team1']
        game_df['Home_Team'] = game_df['Home_Team1']

        # Fill the blank for the 2016 season
        game_df['V_PTS'] = game_df['V_PTS'].replace(r'\s+( +\.)|#', np.nan, regex=True).replace('', np.nan)
        game_df['H_PTS'] = game_df['H_PTS'].replace(r'\s+( +\.)|#', np.nan, regex=True).replace('', np.nan)
        game_df = game_df[game_df.Date.notnull()]
        game_df['V_PTS'].fillna(0, inplace=True)
        game_df['H_PTS'].fillna(1, inplace=True)

        try:
            game_df['Home_Team_PTS'] = game_df['H_PTS'].astype(int)
            game_df['Visitor_Team_PTS'] = game_df['V_PTS'].astype(int)

        # Simulate some True Result for unplayed game in the current season 
        # Avoiding error when making the input_tableau file
        except (ValueError, KeyError) as e:
            game_df['Home_Team_PTS'] = game_df['Home_Team_PTS'].replace([''], 1)
            game_df['Visitor_Team_PTS'] = game_df['Visitor_Team_PTS'].replace([''], 0)
            game_df['Home_Team_PTS'] = game_df['Home_Team_PTS'].astype(int)
            game_df['Visitor_Team_PTS'] = game_df['Visitor_Team_PTS'].astype(int)

        game_df.drop(game_df[[2, 3, 4, 5, 6, 7, 8]], axis=1, inplace=True)

        game_df = game_df[game_df['Date'].str.contains('Playoffs') == False]
        game_df = game_df[game_df['Visitor_Team'].str.contains('None') == False]
        game_df = game_df[game_df['Home_Team'].str.contains('None') == False]

        # Converting the column date to datetime and thus to ease indexing the year
        game_df['Date'] = pd.to_datetime(game_df['Date'], infer_datetime_format=True)

        # ------------Uncomment if you want to filter the dataframe excluding matchups in a span of time-------

        # game_df = game_df[(game_df['Date'].dt.month != 2) & (game_df['Date'].dt.month != 3)\
        #  & (game_df['Date'].dt.month != 4) & (game_df['Date'].dt.month != 5)]

        # ----------------------------------------------------------------------------------------------------------------------

        # Extracting exclusively the 'Date' column to a csv file
        # for further analysis in Tableau with "tableau_input" file
        game_df['Date'].to_csv("date_nba_game_stats_" + str(self.year1) + "_" + str(self.year2) + ".csv", mode='w+',
                               header=False, index=False)

        game_df.drop_duplicates()
        # Dropping the column 'Date' as we do not need it anymore
        game_df.drop('Date', axis=1, inplace=True)

        shift_df = pd.concat(
            [game_df['Season_Yr'], game_df['Visitor_Team'], game_df['Visitor_Team_PTS'], game_df['Home_Team'],
             game_df['Home_Team_PTS']], axis=1)

        game_df = shift_df

        game_df.to_csv("nba_game_stats_" + str(self.year1) + "_" + str(self.year2) + ".csv", index=False, mode='w+')
