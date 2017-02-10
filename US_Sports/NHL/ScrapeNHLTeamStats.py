# coding: utf-8

# In[1]:

import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait


class AcquireNHLTeamStats(object):
    def __init__(self, year1, year2):
        self.year1 = year1
        self.year2 = year2

    def __call__(self):
        # ---------------------------TEAM STATS---------------------------------
        print "=> Scraping Team Stats..."
        self.get_nhl_team_stats_column_headers(self.year1)
        self.get_nhl_team_stats(self.year1, self.year2, self.team_column_headers)
        print "=> Scraping Team Stats...OK"

        # ----------------------CLEANING --------------------------------------
        print "=> Data Cleaning..."
        self.clean_data(self.team_df)
        print "=> Data Cleaning...OK"

    def get_nhl_team_stats_column_headers(self, year1):

        browser = webdriver.Chrome("C:\Users\jbadiabo\PycharmProjects\Sibyl\chromedriver.exe")
        url = "http://www.hockey-reference.com/leagues/NHL_{year1}.html"
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
                WebDriverWait(browser, delay).until(ec.presence_of_element_located((By.ID, "stats")))
            except TimeoutException:
                browser.quit()
                delay += 3
                continue
            break

        table = browser.find_element_by_id('stats')
        head = table.find_element_by_tag_name('thead')

        try:
            head_line = head.find_elements_by_tag_name("tr")[1]
        except:
            head_line = head.find_element_by_tag_name("tr")

        team_column_headers = [header.text.encode("utf8") for header in head_line.find_elements_by_tag_name("th")]
        self.team_column_headers = team_column_headers[1:]

        browser.quit()

    def get_nhl_team_stats(self, year1, year2, team_column_headers):

        url_template = "http://www.hockey-reference.com/leagues/NHL_{year}.html"

        team_df = pd.DataFrame()

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
                    WebDriverWait(browser, delay).until(ec.presence_of_element_located((By.ID, "stats")))
                except TimeoutException:
                    browser.quit()
                    delay += 3
                    continue
                break

            table = browser.find_element_by_id('stats')
            body = table.find_element_by_tag_name('tbody')

            body_rows = body.find_elements_by_tag_name('tr')

            for row in body_rows:
                data = row.find_elements_by_tag_name('td')
                file_row = [datum.text.encode("utf8") for datum in data]

                file_data.append(file_row)

            year_df = pd.DataFrame(file_data, columns=team_column_headers)
            year_df.insert(1, 'Season_Yr', year)
            team_df = team_df.append(year_df, ignore_index=True)

            browser.quit()

            self.team_df = team_df

            # ----------------------------------------------------------------------------------------------
            # -----------------------------------DATA CLEANING---------------------------------------------
            # ----------------------------------------------------------------------------------------------

    def clean_data(self, team_df):

        # Convert the data to the proper data frame
        team_df = team_df.apply(pd.to_numeric, errors="ignore")

        # Get rid of the 'league average' and empty column values rows
        team_df.rename(columns={'': 'Tm'}, inplace=True)
        team_df = team_df[team_df['Tm'] != '']
        team_df = team_df[team_df['Tm'] != 'League Average']
        team_df = team_df[team_df['Tm'].notnull()]

        self.team_df = team_df

        # get the column names and replace all '#' with 'Nb'
        team_df.columns = team_df.columns.str.replace('#', 'Nb_')

        # get the column names and replace all '+' with 'Nb'
        team_df.columns = team_df.columns.str.replace('+', '_Plus')

        # get the column names and replace all '%' with '_Perc'
        team_df.columns = team_df.columns.str.replace('%', '_Perc')

        # and replace all '/' with '_per_'
        team_df.columns = team_df.columns.str.replace('/', '_Per_')

        # Rename duplicates so as to drop them from the df

        cols = pd.Series(team_df.columns)
        for dup in team_df.columns.get_duplicates():
            cols[team_df.columns.get_loc(dup)] = ['dup_' + dup if d_idx != 0 else dup for d_idx in
                                                  range(team_df.columns.get_loc(dup).sum())]

        team_df.columns = cols

        cols = [c for c in team_df.columns if c.lower()[:3] != 'dup']
        team_df = team_df[cols]

        # Get rid of games columns
        team_df.drop('GP', axis=1, inplace=True)
        team_df.drop('PDO', axis=1, inplace=True)
        team_df.drop('AvAge', axis=1, inplace=True)
        team_df.drop('PTS', axis=1, inplace=True)

        # Fill NaN when they exist: useful especially when the current season is still on the beginning
        team_df.fillna(0, inplace=True)

        # Getting rid of the star at the end of several team names
        team_df['Tm'] = team_df['Tm'].str.rstrip('*')

        team_df.to_csv("nhl_team_stats_" + str(self.year1) + '_' + str(self.year2) + '.csv', mode='w+')
