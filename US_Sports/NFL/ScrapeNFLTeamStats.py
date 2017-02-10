# coding: utf-8

# In[8]:

import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait


class AcquireNFLTeamStats(object):
    def __init__(self, year1, year2):
        self.year1 = year1
        self.year2 = year2

    def __call__(self):
        # ---------------------------OFF STATS---------------------------------
        print "=> Scraping off team stats..."
        self.get_nfl_off_team_stats_column_headers(self.year1)
        self.get_nfl_off_team_stats(self.year1, self.year2, self.off_team_column_headers)
        self.get_nfl_off_passing_column_headers(self.year1)
        self.get_nfl_off_passing(self.year1, self.year2, self.off_passing_column_headers)
        self.merge_off_dfs(self.team_offense_df, self.passing_offense_df)
        print "=> Scraping off team stats...OK"

        # -------------------------DEF STATS----------------------------------
        print "=> Scraping def team stats..."
        self.get_nfl_def_team_stats_column_headers(self.year1)
        self.get_nfl_def_team_stats(self.year1, self.year2, self.def_team_column_headers)
        self.get_nfl_def_passing_column_headers(self.year1)
        self.get_nfl_def_passing(self.year1, self.year2, self.def_passing_column_headers)
        self.merge_def_dfs(self.team_defense_df, self.passing_defense_df)
        print "=> Scraping def team stats...OK"

        # -----------------------MERGE-----------------------------------------
        print "Merging off and def dfs..."
        self.merge_off_def_dfs(self.offense_df, self.defense_df)
        print "Merging off and def dfs...OK"

        # ----------------------CLEANING --------------------------------------
        print "Data cleaning..."
        self.clean_data(self.team_df)
        print "Data cleaning...OK"

    def get_nfl_off_team_stats_column_headers(self, year1):

        browser = webdriver.Chrome("C:\Users\jbadiabo\PycharmProjects\Sibyl\chromedriver.exe")

        url = "http://www.pro-football-reference.com/years/{year1}/"
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
                WebDriverWait(browser, delay).until(ec.presence_of_element_located((By.ID, "team_stats")))
            except TimeoutException:
                browser.quit()
                delay += 3
                continue
            break

        table = browser.find_element_by_id('team_stats')
        head = table.find_element_by_tag_name('thead')

        try:
            head_line = head.find_elements_by_tag_name("tr")[1]
        except:
            head_line = head.find_element_by_tag_name("tr")

        off_team_column_headers = [header.text.encode("utf8") for header in head_line.find_elements_by_tag_name("th")]

        self.off_team_column_headers = off_team_column_headers[1:]

        browser.quit()

    def get_nfl_off_team_stats(self, year1, year2, off_team_column_headers):

        url_template = "http://www.pro-football-reference.com/years/{year}/"

        team_offense_df = pd.DataFrame()

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
                    WebDriverWait(browser, delay).until(ec.presence_of_element_located((By.ID, "team_stats")))
                except TimeoutException:
                    browser.quit()
                    delay += 3
                    continue
                break

            table = browser.find_element_by_id('team_stats')
            body = table.find_element_by_tag_name('tbody')

            body_rows = body.find_elements_by_tag_name('tr')

            for row in body_rows:
                data = row.find_elements_by_tag_name('td')
                file_row = [datum.text.encode("utf8") for datum in data]

                file_data.append(file_row)

            year_df = pd.DataFrame(file_data, columns=off_team_column_headers)
            year_df.insert(1, 'Season_Yr', year)
            team_offense_df = team_offense_df.append(year_df, ignore_index=True)

            self.team_offense_df = team_offense_df

            browser.quit()

    # ------------------------------- OFF PASSING  ----------------------------------------------------------
    # -------------------------------------------------------------------------------------------------------

    def get_nfl_off_passing_column_headers(self, year1):

        url = "http://www.pro-football-reference.com/years/{year1}/"
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
                WebDriverWait(browser, delay).until(ec.presence_of_element_located((By.ID, "passing")))
            except TimeoutException:
                browser.quit()
                delay += 3
                continue
            break

        table = browser.find_element_by_id('passing')
        head = table.find_element_by_tag_name('thead')

        try:
            head_line = head.find_elements_by_tag_name("tr")[1]
        except:
            head_line = head.find_element_by_tag_name("tr")

        off_passing_column_headers = [header.text.encode("utf8") for header in
                                      head_line.find_elements_by_tag_name("th")]

        self.off_passing_column_headers = off_passing_column_headers[1:]

        browser.quit()

    def get_nfl_off_passing(self, year1, year2, off_passing_column_headers):

        url_template = "http://www.pro-football-reference.com/years/{year}/"

        passing_offense_df = pd.DataFrame()

        for year in range(year1, year2 + 1):
            passing_file_data = []
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
                    WebDriverWait(browser, delay).until(ec.presence_of_element_located((By.ID, "passing")))
                except TimeoutException:
                    browser.quit()
                    delay += 3
                    continue
                break

            passing_table = browser.find_element_by_id('passing')
            body = passing_table.find_element_by_tag_name('tbody')

            body_rows = body.find_elements_by_tag_name('tr')
            for row in body_rows:
                data = row.find_elements_by_tag_name('td')
                passing_file_row = [datum.text.encode("utf8") for datum in data]

                passing_file_data.append(passing_file_row)

            passing_year_df = pd.DataFrame(passing_file_data, columns=off_passing_column_headers)
            passing_year_df.insert(1, 'Season_Yr', year)
            passing_offense_df = passing_offense_df.append(passing_year_df, ignore_index=True)
            self.passing_offense_df = passing_offense_df

            browser.quit()

            # ---------------------------------------------------------------------------------

    def merge_off_dfs(self, team_offense_df, passing_offense_df):

        offense_df = pd.merge(team_offense_df, passing_offense_df, on=['Tm', 'Season_Yr'], how='inner')

        # get the column names and replace all '_x' with _Off'
        offense_df.columns = offense_df.columns.str.replace('_x', '_Off')

        # get the column names and replace all '_y' with  '_POff'
        offense_df.columns = offense_df.columns.str.replace('_y', '_POff')

        self.offense_df = offense_df

    # ------------------------------------------------------------------------------------------------------------
    # ----------------------------------------------DEFENSE STATS-------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------

    def get_nfl_def_team_stats_column_headers(self, year1):

        url = "http://www.pro-football-reference.com/years/{year1}/opp.htm"
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
                WebDriverWait(browser, delay).until(ec.presence_of_element_located((By.ID, "team_stats")))
            except TimeoutException:
                browser.quit()
                delay += 3
                continue
            break

        table = browser.find_element_by_id('team_stats')
        head = table.find_element_by_tag_name('thead')

        try:
            head_line = head.find_elements_by_tag_name("tr")[1]
        except:
            head_line = head.find_element_by_tag_name("tr")

        def_team_column_headers = [header.text.encode("utf8") for header in head_line.find_elements_by_tag_name("th")]
        self.def_team_column_headers = def_team_column_headers[1:]

        browser.quit()

    def get_nfl_def_team_stats(self, year1, year2, def_team_column_headers):

        url_template = "http://www.pro-football-reference.com/years/{year}/opp.htm"

        team_defense_df = pd.DataFrame()

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
                    WebDriverWait(browser, delay).until(ec.presence_of_element_located((By.ID, "team_stats")))
                except TimeoutException:
                    browser.quit()
                    delay += 3
                    continue
                break

            table = browser.find_element_by_id('team_stats')
            body = table.find_element_by_tag_name('tbody')

            body_rows = body.find_elements_by_tag_name('tr')

            for row in body_rows:
                data = row.find_elements_by_tag_name('td')
                file_row = [datum.text.encode("utf8") for datum in data]

                file_data.append(file_row)

            year_df = pd.DataFrame(file_data, columns=def_team_column_headers)
            year_df.insert(1, 'Season_Yr', year)
            team_defense_df = team_defense_df.append(year_df, ignore_index=True)

            self.team_defense_df = team_defense_df

            browser.quit()

    # ----------------------------------- DEF PASSING ------------------------------------------------------
    # -------------------------------------------------------------------------------------------------------

    def get_nfl_def_passing_column_headers(self, year1):

        url = "http://www.pro-football-reference.com/years/{year1}/opp.htm"
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
                WebDriverWait(browser, delay).until(ec.presence_of_element_located((By.ID, "passing")))
            except TimeoutException:
                browser.quit()
                delay += 3
                continue
            break

        table = browser.find_element_by_id('passing')
        head = table.find_element_by_tag_name('thead')

        try:
            head_line = head.find_elements_by_tag_name("tr")[1]
        except:
            head_line = head.find_element_by_tag_name("tr")

        def_passing_column_headers = [header.text.encode("utf8") for header in
                                      head_line.find_elements_by_tag_name("th")]

        self.def_passing_column_headers = def_passing_column_headers[1:]

        browser.quit()

    def get_nfl_def_passing(self, year1, year2, def_passing_column_headers):

        url_template = "http://www.pro-football-reference.com/years/{year}/opp.htm"

        passing_defense_df = pd.DataFrame()

        for year in range(year1, year2 + 1):

            passing_file_data = []

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
                    WebDriverWait(browser, delay).until(ec.presence_of_element_located((By.ID, "passing")))
                except TimeoutException:
                    browser.quit()
                    delay += 3
                    continue
                break

            passing_table = browser.find_element_by_id('passing')
            body = passing_table.find_element_by_tag_name('tbody')

            body_rows = body.find_elements_by_tag_name('tr')
            for row in body_rows:
                data = row.find_elements_by_tag_name('td')
                passing_file_row = [datum.text.encode("utf8") for datum in data]

                passing_file_data.append(passing_file_row)

            passing_year_df = pd.DataFrame(passing_file_data, columns=def_passing_column_headers)
            passing_year_df.insert(1, 'Season_Yr', year)
            passing_defense_df = passing_defense_df.append(passing_year_df, ignore_index=True)

            self.passing_defense_df = passing_defense_df

            browser.quit()

    def merge_def_dfs(self, team_defense_df, passing_defense_df):

        defense_df = pd.merge(team_defense_df, passing_defense_df, on=['Tm', 'Season_Yr'], how='inner')

        # get the column names and replace all '_x' with _Def'
        defense_df.columns = defense_df.columns.str.replace('_x', '_Def')

        # get the column names and replace all '_y' with  '_PDef'
        defense_df.columns = defense_df.columns.str.replace('_y', '_PDef')

        self.defense_df = defense_df

    # ----------------------------------------MERGE ALL-----------------------------------------------------------

    def merge_off_def_dfs(self, offense_df, defense_df):

        team_df = pd.merge(offense_df, defense_df, on=['Tm', 'Season_Yr'], how='inner')

        self.team_df = team_df

    # ----------------------------------------------------------------------------------------------
    # -----------------------------------DATA CLEANING---------------------------------------------
    # ----------------------------------------------------------------------------------------------

    def clean_data(self, team_df):
        team_df.columns = team_df.columns.str.replace('_x', '_Off')
        team_df.columns = team_df.columns.str.replace('_y', '_Def')

        # Convert the data to the proper data frame
        team_df = team_df.apply(pd.to_numeric, errors="ignore")

        # Get rid of the 'league average' and empty column values rows
        team_df = team_df[team_df.Tm != 'Avg Team']
        team_df = team_df[team_df.Tm != '']
        team_df = team_df[team_df.Tm.notnull()]

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
        team_df.drop('G_Off', axis=1, inplace=True)
        team_df.drop('G_Def', axis=1, inplace=True)
        team_df.drop('G_POff', axis=1, inplace=True)
        team_df.drop('G_PDef', axis=1, inplace=True)

        # Fill NaN when they exist: when the current season is still on the beginning
        team_df.fillna(0, inplace=True)

        self.team_df = team_df

        team_df.to_csv("nfl_team_stats_" + str(self.year1) + '_' + str(self.year2) + '.csv', mode='w+')
