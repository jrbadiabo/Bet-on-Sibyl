# coding: utf-8

# In[7]:

from urllib import urlopen

import pandas as pd
from bs4 import BeautifulSoup


class AcquireGameStats(object):
    # Creates a csv file containing all the matchup results between
    # NBA teams for all seasons between inputs 'year1' and 'year2'.
    # Nb: Below - Uncomment if you want to filter the dataframe excluding matchups in a span of time
    # When you finished to make your modif'
    # do not forget to convert your file in '.py' to make it usesable as class in other programs

    def __init__(self, year0, year1, year2, csv_filename, csv_datetime_filename):
        self.year0 = year0
        self.year1 = year1
        self.year2 = year2
        self.csv_filename = csv_filename
        self.csv_datetime_filename = csv_datetime_filename

    def __call__(self):
        print "Scraping game data..."
        self.get_gs_column_headers(self.year0)
        self.get_game_data(self.year1, self.year2, self.gs_column_headers)
        self.clean_gs_data(self.game_df, self.csv_datetime_filename)
        self.gs_write_to_csv(self.csv_filename, self.game_df)
        print "Scraping game data...OK"

    # Getting the column headers
    def get_gs_column_headers(self, year0):
        html_page = urlopen(
            'http://www.baseball-reference.com/teams/BAL/{year0}-schedule-scores.shtml'.format(year0=year0))
        soup = BeautifulSoup(html_page, "html5lib")
        right_table = soup.find('table', id="team_schedule")
        self.gs_column_headers = [th.getText() for th in right_table.find_all('tr', limit=1)[0].find_all('th')]

    # Getting game data from year1 to year2
    def get_game_data(self, year1, year2, gs_column_headers):

        teams = ['ANA', 'ARI', 'ATL', 'BAL', 'BOS', 'CAL', 'CHC', 'CHW', 'CIN', 'CLE', 'COL', 'DET', 'FLA', 'HOU',
                 'KCR', 'LAA', 'LAD', 'MIA', 'MIL', 'MIN', 'MON', 'NYM', 'NYY', 'OAK', 'PHI', 'PIT', 'SDP', 'SEA',
                 'SEP', 'SFG', 'STL', 'TBD', 'TBR', 'TEX', 'TOR', 'WSA', 'WSN']

        url_template = "http://www.baseball-reference.com/teams/{team}/{year}-schedule-scores.shtml"

        game_df = pd.DataFrame()

        for year in range(year1, year2 + 1):
            for team in teams:
                url = url_template.format(year=year, team=team)
                html = urlopen(url)
                soup = BeautifulSoup(html, 'html5lib')

                # Forming the yearly game data table
                try:
                    right_table = soup.find('table', id='team_schedule')
                    data_rows = right_table.find_all('tr')[1:]
                    game_data = [[td.getText() for td in data_rows[i].find_all('td')] for i in range(len(data_rows))]
                    year_df = pd.DataFrame(game_data, columns=gs_column_headers)
                    year_df['Date'] = year_df['Date'].astype(str) + ', ' + str(year)

                    # Append the data to the big data frame
                    game_df = game_df.append(year_df, ignore_index=True)
                    self.game_df = game_df
                except:
                    continue

    # Cleaning the data
    def clean_gs_data(self, game_df, csv_datetime_filename):

        # Removing games played away to avoid duplicate in the big data frame
        game_df = game_df[game_df.iloc[:, 5] != '@']
        # Dropping several columns we do not need 
        game_df.drop(game_df.columns[[0, 1, 3, 5, 7, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]], axis=1, inplace=True)
        # Remove row with missing values at the 'Visitor_Team' column
        game_df = game_df[game_df.Tm.notnull()]
        # Preprocessing the 'Date' column to convert it to datetime format
        game_df['Date'] = game_df.Date.str.replace('Monday,?', '')
        game_df['Date'] = game_df.Date.str.replace('Tuesday,?', '')
        game_df['Date'] = game_df.Date.str.replace('Wednesday,?', '')
        game_df['Date'] = game_df.Date.str.replace('Thursday,?', '')
        game_df['Date'] = game_df.Date.str.replace('Friday,?', '')
        game_df['Date'] = game_df.Date.str.replace('Saturday,?', '')
        game_df['Date'] = game_df.Date.str.replace('Sunday,?', '')
        game_df['Date'] = game_df.Date.str.strip().str.replace(' ', ', ', 1)
        #  syntactic sugar for Series.apply(lambda x: re.sub(r"\(.*\)", "", x))
        game_df['Date'] = game_df.Date.str.replace(r"\(.*\)", "")
        # Converting the column date to datetime and thus to ease indexing the year
        game_df['Date'] = pd.to_datetime(game_df['Date'], infer_datetime_format=True)
        # Renaming the column names
        game_df.insert(1, 'Visitor_Team', game_df['Opp'])
        game_df.insert(2, 'V_PTS', game_df['RA'])
        game_df.insert(3, 'Home_Team', game_df['Tm'])
        game_df.insert(4, 'H_PTS', game_df['R'])
        game_df.drop(game_df.columns[[5, 6, 7, 8]], axis=1, inplace=True)
        # Convert game points to integer
        try:
            game_df['H_PTS'] = game_df['H_PTS'].astype(int)
            game_df['V_PTS'] = game_df['V_PTS'].astype(int)

        # Simulate some True Result for unplayed game in the current season 
        # Avoiding error when making the input_tableau file
        except (ValueError, KeyError) as e:
            game_df['V_PTS'] = game_df['V_PTS'].replace([''], 0)
            game_df['H_PTS'] = game_df['H_PTS'].replace(['Game Preview, Matchups, and Tickets'], 1)
            game_df['H_PTS'] = game_df['H_PTS'].astype(int)
            game_df['V_PTS'] = game_df['V_PTS'].astype(int)

        # Remove duplicates as some issue may happen when uploading in sqlite
        game_df.drop_duplicates(inplace=True)

        # -----------------Uncomment if you want to filter the dataframe excluding matchups in a span of time----------

        # game_df = game_df[(game_df['Date'].dt.month != 2) & (game_df['Date'].dt.month != 3)
        # & (game_df['Date'].dt.month != 4) & (game_df['Date'].dt.month != 5)]

        # ----------------------------------------------------------------------------------------------------------------------

        # Extracting exclusively the 'Date' column to a csv file
        #  for further analysis in Tableau with "tableau_input" file
        game_df['Date'].to_csv(csv_datetime_filename, mode='w+', header=False, index=False)

        # Indexing the Year to create a column 'Season_Yr' for then easing the indexing way in sqlite "Team" + "Year"
        game_df.insert(1, 'Season_Yr', game_df['Date'].apply(lambda x: x.year))
        # Dropping the column 'Date' as we do not need it anymore
        game_df.drop('Date', axis=1, inplace=True)

        self.game_df = game_df

    # Writing the csv file
    def gs_write_to_csv(self, csv_filename, game_df):

        game_df.to_csv(csv_filename, mode='w+', index=False)


if __name__ == '__main__':
    mlb_gamedata = AcquireGameStats(2016, 2016, 2016, "mlb_game_stats_2016.csv",
                                    "mlb_datetime_2016.csv")
    mlb_gamedata()
