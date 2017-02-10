# coding: utf-8

# In[1]:

from urllib import urlopen

import pandas as pd
from bs4 import BeautifulSoup


class AcquireTeamStats(object):
    # Creates a csv file containing cummulative data by season for each
    # NBA team that played games between input 'year1' and 'year2'.
    # When you finished to make your modif' do not forget to convert
    # your file in '.py' to make it usesable as class in other programs

    def __init__(self, year0, year1, year2, csv_filename):
        self.year0 = year0
        self.year1 = year1
        self.year2 = year2
        self.csv_filename = csv_filename

    def __call__(self):
        # --------------------------Batting Stats---------------------------------
        print "=> Scraping Batting Stats..."
        self.get_batting_column_headers(self.year0)
        self.get_batting_team_stats(self.year1, self.year2, self.batting_column_headers)
        self.clean_batting_data(self.batting_season_df)
        print "=> Scraping Batting Stats...OK"
        # --------------------------Pitching Stats---------------------------------
        print "=> Scraping Pitching Stats..."
        self.get_pitching_column_headers(self.year0)
        self.get_pitching_team_stats(self.year1, self.year2, self.pitching_column_headers)
        self.clean_pitching_data(self.pitching_season_df)
        print " Scraping Pitching Stats...OK"
        # ------------------------Merge Data Frames & Write to csv----------------
        self.write_to_csv(self.csv_filename, self.batting_season_df, self.pitching_season_df)

    # ----------------------------BATTING FUNCTIONS------------------------------------
    # Getting the column headers via the 'year0' Team Stats webpage
    def get_batting_column_headers(self, year0):
        html_page = urlopen('http://www.baseball-reference.com/leagues/MLB/{year0}.shtml'.format(year0=year0))
        soup = BeautifulSoup(html_page, "html5lib")

        # Indexing the right table
        right_table = soup.find('table', id="teams_standard_batting")

        # Getting the column headers
        # extracting the text and construct a list of the column headers using list comprehension
        self.batting_column_headers = [th.getText() for th in right_table.find_all('tr', limit=1)[0].find_all('th')]

    # Get the team stats
    def get_batting_team_stats(self, year1, year2, batting_column_headers):

        # creating a url template that will allow us to access the web page for each year
        url_template = "http://www.baseball-reference.com/leagues/MLB/{year}.shtml"

        # create the empty all season dataframe
        batting_season_df = pd.DataFrame()

        for year in range(year1, year2 + 1):
            url = url_template.format(year=year)  # for each year
            html = urlopen(url)  # get the url
            soup = BeautifulSoup(html, 'html5lib')  # Creating a BS object

            # Indexing the right table
            right_table = soup.find('table', id="teams_standard_batting")

            # Get the player data
            data_rows = right_table.find_all('tr')[1:]
            player_data = [[td.getText() for td in data_rows[i].find_all('td')] for i in range(len(data_rows))]

            # Turn yearly data into a data frame
            year_df = pd.DataFrame(player_data, columns=batting_column_headers)
            # Insert and deleting some columns
            year_df.insert(1, 'Season_Yr', year)

            # Append the data to the big data frame
            batting_season_df = batting_season_df.append(year_df, ignore_index=True)

        self.batting_season_df = batting_season_df

    # -----------------------------------------PITCHING FUNCTIONS--------------------------------


    # Getting the column headers via the 'year0' Team Stats webpage
    def get_pitching_column_headers(self, year0):
        html_page = urlopen('http://www.baseball-reference.com/leagues/MLB/{year0}.shtml'.format(year0=year0))
        soup = BeautifulSoup(html_page, "html5lib")

        # Indexing the right table
        right_table = soup.find('table', id="teams_standard_pitching")
        self.pitching_column_headers = [th.getText() for th in right_table.find_all('tr', limit=1)[0].find_all('th')]
        # Getting the column headers
        # extracting the text and construct a list of the column headers using list comprehension

    # Get the team stats
    def get_pitching_team_stats(self, year1, year2, pitching_column_headers):

        # creating a url template that will allow us to access the web page for each year
        url_template = "http://www.baseball-reference.com/leagues/MLB/{year}.shtml"

        # create the empty all season dataframe
        pitching_season_df = pd.DataFrame()

        for year in range(year1, year2 + 1):
            url = url_template.format(year=year)  # for each year
            html = urlopen(url)  # get the url
            soup = BeautifulSoup(html, 'html5lib')  # Creating a BS object

            # Indexing the right table
            right_table = soup.find('table', id="teams_standard_pitching")

            # Get the player data
            data_rows = right_table.find_all('tr')[1:]
            player_data = [[td.getText() for td in data_rows[i].find_all('td')] for i in range(len(data_rows))]

            # Turn yearly data into a data frame
            year_df = pd.DataFrame(player_data, columns=pitching_column_headers)
            # Insert and deleting some columns
            year_df.insert(1, 'Season_Yr', year)

            # Append the data to the big data frame
            pitching_season_df = pitching_season_df.append(year_df, ignore_index=True)

        self.pitching_season_df = pitching_season_df

    def clean_batting_data(self, batting_season_df):

        # Convert the data to the proper data frame
        batting_season_df = batting_season_df.apply(pd.to_numeric, errors="ignore")

        # Get rid of the 'league average' and empty column values rows
        batting_season_df = batting_season_df[batting_season_df.Tm != 'LgAvg']
        batting_season_df = batting_season_df[batting_season_df.Tm != '']
        batting_season_df = batting_season_df[batting_season_df.Tm.notnull()]

        # Rename the columns
        # get the column names and replace all '%' with '_Perc'
        batting_season_df.columns = batting_season_df.columns.str.replace('%', '_Perc')

        # get the column names and replace all '#' with 'Nb'
        batting_season_df.columns = batting_season_df.columns.str.replace('#', 'Nb_')

        # get the column names and replace all '+' with 'Nb'
        batting_season_df.columns = batting_season_df.columns.str.replace('+', '_Plus')

        # and replace all '/' with '_per_'
        batting_season_df.columns = batting_season_df.columns.str.replace('/', '_per_')

        # Delete the columns we do not need in both data frames
        if 'BatAge' in batting_season_df.columns:
            batting_season_df.drop('BatAge', axis='columns', inplace=True)
        if 'Nb_Bat' in batting_season_df.columns:
            batting_season_df.drop('Nb_Bat', axis='columns', inplace=True)
        if 'G' in batting_season_df.columns:
            batting_season_df.drop('G', axis='columns', inplace=True)
        if 'W' in batting_season_df.columns:
            batting_season_df.drop('W', axis='columns', inplace=True)
        if 'L' in batting_season_df.columns:
            batting_season_df.drop('L', axis='columns', inplace=True)
        if 'GS' in batting_season_df.columns:
            batting_season_df.drop('GS', axis='columns', inplace=True)
        if 'GF' in batting_season_df.columns:
            batting_season_df.drop('GF', axis='columns', inplace=True)
        if 'Nb_P' in batting_season_df.columns:
            batting_season_df.drop('Nb_P', axis='columns', inplace=True)

        self.batting_season_df = batting_season_df

    def clean_pitching_data(self, pitching_season_df):

        # Convert the data to the proper data frame
        pitching_season_df = pitching_season_df.apply(pd.to_numeric, errors="ignore")

        # Get rid of the 'league average' and empty column values rows
        pitching_season_df = pitching_season_df[pitching_season_df.Tm != 'LgAvg']
        pitching_season_df = pitching_season_df[pitching_season_df.Tm != '']
        pitching_season_df = pitching_season_df[pitching_season_df.Tm.notnull()]

        # Rename the columns
        # replace the 'W/L%' by 'WinLoss%' to avoid the '_' which seems to cause trouble in table operations
        pitching_season_df.columns = pitching_season_df.columns.str.replace('W-L%', 'WinLoss%')

        # get the column names and replace all '%' with '_Perc'
        pitching_season_df.columns = pitching_season_df.columns.str.replace('%', '_Perc')

        # get the column names and replace all '#' with 'Nb'
        pitching_season_df.columns = pitching_season_df.columns.str.replace('#', 'Nb_')

        # get the column names and replace all '+' with 'Nb'
        pitching_season_df.columns = pitching_season_df.columns.str.replace('+', '_Plus')

        # and replace all '/' with '_per_'
        pitching_season_df.columns = pitching_season_df.columns.str.replace('/', '_per_')

        # Delete the columns we do not need in both data frames
        if 'PAge' in pitching_season_df.columns:
            pitching_season_df.drop('PAge', axis='columns', inplace=True)
        if 'G' in pitching_season_df.columns:
            pitching_season_df.drop('G', axis='columns', inplace=True)
        if 'W' in pitching_season_df.columns:
            pitching_season_df.drop('W', axis='columns', inplace=True)
        if 'L' in pitching_season_df.columns:
            pitching_season_df.drop('L', axis='columns', inplace=True)
        if 'GS' in pitching_season_df.columns:
            pitching_season_df.drop('GS', axis='columns', inplace=True)
        if 'GF' in pitching_season_df.columns:
            pitching_season_df.drop('GF', axis='columns', inplace=True)
        if 'Nb_P' in pitching_season_df.columns:
            pitching_season_df.drop('Nb_P', axis='columns', inplace=True)
        if 'Tm' in pitching_season_df.columns:
            pitching_season_df.drop('Tm', axis='columns', inplace=True)
        if 'Season_Yr' in pitching_season_df.columns:
            pitching_season_df.drop('Season_Yr', axis='columns', inplace=True)

        self.pitching_season_df = pitching_season_df

    def write_to_csv(self, csv_filename, batting_season_df, pitching_season_df):
        # Concatenate both batting and pitching data frames
        big_df = pd.concat([batting_season_df, pitching_season_df], axis=1)

        # Rename duplicates as some issue may happen when uploading in sqlite
        cols = pd.Series(big_df.columns)
        for dup in big_df.columns.get_duplicates():
            cols[big_df.columns.get_loc(dup)] = [
                'P_' + dup if d_idx != 0 else 'B_' + dup for d_idx in
                range(big_df.columns.get_loc(dup).sum())]
        big_df.columns = cols

        big_df.to_csv(csv_filename, mode='w+')
