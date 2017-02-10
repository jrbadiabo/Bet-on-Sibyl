# coding: utf-8

# In[20]:

import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait


class AcquireNBATeamStats(object):
    def __init__(self, year1, year2):
        self.year1 = year1
        self.year2 = year2

    def __call__(self):
        # ---------------------------TEAM STATS-----------------------
        print "Scraping Team Stats..."
        self.get_nba_team_stats(self.year1, self.year2)
        print "Scraping Team Stats...OK"

        # ----------------------CLEANING -----------------------------
        print "Data cleaning..."
        self.clean_data(self.team_df)
        print "Data cleaning...OK"

    def get_nba_team_stats(self, year1, year2):

        browser = webdriver.Chrome("C:\Users\jbadiabo\PycharmProjects\Sibyl\chromedriver.exe")
        url = "http://www.basketball-reference.com/leagues/NBA_{year1}.html"
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
                WebDriverWait(browser, delay).until(ec.presence_of_element_located((By.ID, "misc_stats")))
            except TimeoutException:
                browser.quit()
                continue
            break

        browser.maximize_window()

        table = browser.find_element_by_id('misc_stats')
        head = table.find_element_by_tag_name('thead')

        head_line = head.find_elements_by_tag_name("tr")[1]

        team_column_headers = [header.text.encode("utf8") for header in head_line.find_elements_by_tag_name("th")]
        team_column_headers = team_column_headers[1:]

        url_template = "http://www.basketball-reference.com/leagues/NBA_{year}.html"

        team_df = pd.DataFrame()

        browser.quit()

        browser = webdriver.Chrome("C:\Users\jbadiabo\PycharmProjects\Sibyl\chromedriver.exe")

        for year in range(year1, year2 + 1):
            file_data = []
            url = url_template.format(year=year)

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
                    WebDriverWait(browser, delay).until(ec.presence_of_element_located((By.ID, "misc_stats")))
                except TimeoutException:
                    browser.quit()
                    continue
                break

            browser.maximize_window()

            table = browser.find_element_by_id('misc_stats')
            body = table.find_element_by_tag_name('tbody')

            body_rows = body.find_elements_by_tag_name('tr')

            for row in body_rows:
                data = row.find_elements_by_tag_name('td')
                file_row = [datum.text.encode("utf8") for datum in data]

                file_data.append(file_row)

            year_df = pd.DataFrame(file_data, columns=team_column_headers)
            year_df.insert(1, 'Season_Yr', year)
            team_df = team_df.append(year_df, ignore_index=True)

            try:

                next_page = browser.find_element_by_css_selector(".button2.next")

                next_page.click()

                try:
                    WebDriverWait(browser, delay).until(ec.presence_of_element_located((By.ID, "team_stats")))
                except TimeoutException as ex:
                    print ex.message
            except:
                continue

        browser.quit()

        self.team_df = team_df

    # ----------------------------------------------------------------------------------------------
    # -----------------------------------DATA CLEANING---------------------------------------------
    # ----------------------------------------------------------------------------------------------

    def clean_data(self, team_df):

        # Convert the data to the proper data frame
        team_df = team_df.apply(pd.to_numeric, errors="ignore")

        # Get rid of the 'league average' rows
        team_df = team_df[team_df.Team != 'League Average']

        # Rename the columns
        # get the column names and replace all '%' with '_Perc'
        team_df.columns = team_df.columns.str.replace('%', '_Perc')

        # and replace all '/' with '_per_'
        team_df.columns = team_df.columns.str.replace('/', '_per_')

        # get the column names and replace all '#' with 'Nb'
        team_df.columns = team_df.columns.str.replace('#', 'Nb_')

        # get the column names and replace all '+' with 'Nb'
        team_df.columns = team_df.columns.str.replace('+', '_Plus')

        # Rename duplicates as some issue may happen when uploading in sqlite
        cols = pd.Series(team_df.columns)
        for dup in team_df.columns.get_duplicates():
            cols[team_df.columns.get_loc(dup)] = ['D_' + dup if d_idx != 0 else 'O_' + dup for d_idx in
                                                  range(team_df.columns.get_loc(dup).sum())]
        team_df.columns = cols

        # Getting rid of the star at the end of several team names
        team_df['Team'] = team_df['Team'].str.rstrip('*')

        # Inserting a Winning percentage 'WP' based on the Pythagorean Win-Loss columns
        team_df.insert(3, 'WP', team_df['PW'] / (team_df['PW'] + team_df['PL']))
        team_df['WP'] = team_df['WP'].round(3)

        # Then, dropping the Pythagorean Win-Loss columns since we don't need it anymore
        team_df.drop('PW', axis=1, inplace=True)
        team_df.drop('PL', axis=1, inplace=True)

        # Getting rid of the 'Age' column after reading the article 
        # 'http://www.sbnation.com/2014/4/2/5573666/nba-experience-age-dallas-mavericks-miami-heat'
        team_df.drop('Age', axis=1, inplace=True)

        # same thing for the 'Attendance' column 
        team_df.drop('Attendance', axis=1, inplace=True)
        team_df.drop('Arena', axis=1, inplace=True)

        # Fill NaN when they exist: useful especially when the current season is still on the beginning
        team_df.fillna(0, inplace=True)

        team_df.to_csv("nba_team_stats_" + str(self.year1) + '_' + str(self.year2) + '.csv', mode='w+')
