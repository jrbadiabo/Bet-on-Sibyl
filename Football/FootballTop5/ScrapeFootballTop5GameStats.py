# coding: utf-8

# In[17]:

import unicodedata

import pandas as pd
from dateutil.relativedelta import relativedelta
from selenium import webdriver
from selenium.common.exceptions import TimeoutException


class AcquireFootballTop5GameStats(object):
    def __init__(self, year1, year2):
        self.year1, self.year2 = year1, year2

    def __call__(self):
        self.get_football_top5_game_stats(self.year1, self.year2)
        self.clean_football_top5_game_stats(self.game_df)

    # -----------------------------------------------------------------------------------------------------------------------------

    def get_football_top5_game_stats(self, year1, year2):

        game_df = pd.DataFrame()
        matchup_league_df = pd.DataFrame()
        countries = ['germany', 'spain', 'italy', 'england', 'france']
        leagues = ['bundesliga', 'primera-division', 'serie-a', 'premier-league', 'ligue-1']
        url_template = "http://www.soccerstats.com/results.asp?league={country}_{year}"
        url_template_cs = "http://www.soccerstats.com/results.asp?league={country}"
        all_matchup_league = []

        for country, league in zip(countries, leagues):

            for year in range(year1, year2 + 1):

                browser = webdriver.Chrome("C:\Users\jbadiabo\PycharmProjects\Sibyl\chromedriver.exe")

                if year == 2017:
                    url = url_template_cs.format(country=country)
                else:
                    url = url_template.format(country=country, year=year)

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
                    except TimeoutException:
                        browser.quit()
                        continue
                    break

                file_data = []
                matchup_league = []

                table = browser.find_element_by_id('btable')

                body = table.find_element_by_tag_name('tbody')
                body_rows = body.find_elements_by_class_name('odd')

                for row in body_rows:
                    data = row.find_elements_by_tag_name('td')
                    file_row = [datum.text.encode('utf8') for datum in data]
                    file_row = [datum.decode('utf8') for datum in file_row]
                    file_row = [unicodedata.normalize('NFD', datum).encode('ascii', 'ignore') for datum in file_row]

                    file_data.append(file_row)

                    matchup_league.append(league)

                year_df = pd.DataFrame(file_data)
                all_matchup_league.extend(matchup_league)
                year_df.insert(0, 'Season_Yr', year)
                year_df.drop(year_df.columns[[2, 5, 6, 7, 8]], axis=1, inplace=True)

                game_df = game_df.append(year_df, ignore_index=True)

                browser.quit()

        matchup_league_df = matchup_league_df.append(all_matchup_league)
        matchup_league_df.to_csv("football_top5_matchup_league_" + str(self.year1) + "_" + str(self.year2) + ".csv",
                                 header=False, index=False, encoding="utf-8", mode='w+')

        self.matchup_league_df = matchup_league_df
        self.game_df = game_df

    def clean_football_top5_game_stats(self, game_df):

        game_df.columns = ['Season_Yr', 'Date', 'Matchup', 'Score']
        game_df['Season_Yr'] = game_df['Season_Yr'].astype(str)

        # In the column 'raw', extract xxxx xx xx in the strings
        game_df['Date'] = game_df['Date'].str.split(' ', 1).str[1]
        game_df['Date'] = game_df['Date'] + ' ' + game_df['Season_Yr']
        game_df['Date'] = game_df['Date'].str.replace('.', '')
        game_df['Date'] = game_df['Date'].str.strip()
        game_df['Date'] = pd.to_datetime(game_df['Date'], infer_datetime_format=True)
        game_df['Date'] = game_df['Date'].apply(lambda x: x - relativedelta(years=1) if 8 <= x.month <= 12 else x)

        game_df['Home'], game_df['Visitor'] = game_df['Matchup'].str.split(' - ', 1).str

        game_df['Visitor_Team'] = game_df['Visitor']
        game_df['Visitor_Team_PTS'] = game_df['Score'].str.split(' - ', 1).str[1]
        game_df['Visitor_Team_PTS'] = game_df['Visitor_Team_PTS'].str.strip()

        game_df['Home_Team'] = game_df['Home']
        game_df['Home_Team_PTS'] = game_df['Score'].str.split(' - ', 1).str[0]
        game_df['Home_Team_PTS'] = game_df['Home_Team_PTS'].str.strip()

        game_df.drop('Home', axis=1, inplace=True)
        game_df.drop('Visitor', axis=1, inplace=True)

        game_df = game_df.drop('Matchup', axis=1)
        game_df = game_df.drop('Score', axis=1)

        game_df['Visitor_Team_PTS'].fillna(0, inplace=True)
        game_df['Home_Team_PTS'].fillna(0, inplace=True)

        try:
            game_df['Home_Team_PTS'] = game_df['Home_Team_PTS'].astype(int)
            game_df['Visitor_Team_PTS'] = game_df['Visitor_Team_PTS'].astype(int)

        # Simulate some True Result for unplayed game in the current season
        # Avoiding error when making the input_tableau file
        except (ValueError, KeyError) as e:
            game_df['Home_Team_PTS'] = game_df['Home_Team_PTS'].replace(['-'], 0)
            game_df['Home_Team_PTS'] = game_df['Home_Team_PTS'].replace([''], 0)
            try:
                game_df['Home_Team_PTS'] = game_df['Home_Team_PTS'].replace(['pp.'], 0)
            except:
                pass
            game_df['Home_Team_PTS'] = game_df['Home_Team_PTS'].astype(int)
            game_df['Visitor_Team_PTS'] = game_df['Visitor_Team_PTS'].astype(int)

        # Forcing the column value stripping process due to some problems when sending data to the db
        game_df.columns = game_df.columns.str.strip()

        game_df['Visitor_Team'] = game_df['Visitor_Team'].str.lstrip()
        game_df['Visitor_Team'] = game_df['Visitor_Team'].str.strip()

        game_df['Home_Team'] = game_df['Home_Team'].str.lstrip()
        game_df['Home_Team'] = game_df['Home_Team'].str.strip()

        # Extracting exclusively the 'Date' column
        # to a csv file for further analysis in Tableau with "tableau_input" file
        game_df['Date'].to_csv("date_football_top5_game_stats_" + str(self.year1) + "_" + str(self.year2) + ".csv",
                               mode='w+', header=False, index=False)

        # Dropping the column 'Date' as we do not need it anymore
        game_df.drop('Date', axis=1, inplace=True)

        game_df.to_csv("football_top5_game_stats_" + str(self.year1) + "_" + str(self.year2) + ".csv", index=False,
                       encoding="utf-8", mode='w+')

# ex of use x = AcquireFootballTop5GameStats(2013, 2016)
# x()
