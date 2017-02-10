# coding: utf-8

# In[154]:
import itertools
from datetime import timedelta
import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait


# get_ipython().magic(u'matplotlib inline')


def fix_str(s):
    s = s.strip()
    if ':' in s:
        if 'OT' in s: s = s[:s.find('OT')].strip()  # Used for basketball model
        s = s.split(':')
        s = [int(_) for _ in s]
        s = [str(_) for _ in s]
        s = ' '.join(s)


def fix_odds(s):
    try:
        if '+' in s:
            return str(float(s[1:]) / 100 + 1)
        elif '-' in s:
            return str((float(s[1:]) + 100) / float(s[1:]))
        elif '/' in s:
            s = s.strip()
            return str((float(s[:s.find('/')]) / float(s[s.find('/') + 1:]) + 1.0))
        elif '.' in s:
            return s
        else:
            print s
            return 1.0
    except:
        return 1.0


class AcquireMatchupDatetimeOddsTwoChoices(object):
    # -------------------------------------------------------------------------------------------------------------------------------------

    def __init__(self, season_over, betbrain_upcoming_games_url, cs_team_stats_filename, league_name,
                 tableau_filename, upcoming_games_output_filename_us, upcoming_games_output_filename_eu):
        self.betbrain_upcoming_games_url = betbrain_upcoming_games_url
        self.cs_team_stats_filename = cs_team_stats_filename
        self.league_name = league_name
        self.tableau_filename = tableau_filename
        self.upcoming_games_output_filename_us = upcoming_games_output_filename_us
        self.upcoming_games_output_filename_eu = upcoming_games_output_filename_eu
        self.season_over = season_over

    def __call__(self):
        # Within "generate_data" we check if there is any matchup in the league
        # If not an exception will be raised and we will pass the script and
        # change the from 'No' to 'Yes' allowing us to pass in a more pythonic
        # way the other class methods
        print "Scraping relevant data from betbrain"
        try:
            self.generate_data(self.betbrain_upcoming_games_url)
        except TimeoutException:
            print self.league_name + " season is over => Skipping the Betbrain scrapping step\n"
            self.season_over = 'Yes'
            pass

        if self.season_over == 'No':
            self.clean_data(self.game_df, self.league_name)
            self.merge_with_tableau_output(self.game_df, self.tableau_filename, self.upcoming_games_output_filename_us,
                                           self.upcoming_games_output_filename_eu)
        else:
            pass

    # -------------------------------------------------------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------------------------------------------------------

    def generate_data(self, betbrain_upcoming_games_url):

        delay = 5

        while True:

            try:
                browser = webdriver.Chrome("C:\Users\jbadiabo\PycharmProjects\Sibyl\chromedriver.exe")
                browser.get(betbrain_upcoming_games_url)
                WebDriverWait(browser, delay).until(ec.presence_of_element_located((By.CLASS_NAME, "SportsBox")))

            except TimeoutException:
                browser.quit()
                delay += 3
                continue

            break

        # Checking if there is matchups in this league
        # If not this block of code will raise exception and we will pass this script
        WebDriverWait(browser, delay).until(ec.presence_of_element_located((By.CLASS_NAME, "MatchesList")))
        table_check = browser.find_element_by_class_name("MatchesList")
        body_rows = table_check.find_elements_by_class_name("Match")

        browser.maximize_window()

        file_dates = []
        file_matchups = []
        file_odds = []

        for row in body_rows:
            date = row.find_element_by_class_name('DateTime')
            date = [date.text.encode('utf-8')]
            file_dates.append(date)

            matchup = row.find_element_by_class_name('MatchDetails')
            matchup_d1 = matchup.find_element_by_class_name('MatchTitleLink')
            matchup_d1 = [matchup_d1.text.encode('utf-8')]
            file_matchups.append(matchup_d1)

            odds_list = row.find_element_by_class_name('BetList')
            odds = odds_list.find_elements_by_class_name('Bet')
            file_odds_xy = []
            for odd in odds:
                odd_w = odd.find_elements_by_class_name("AverageOdds")
                odd_x = [fix_odds(x.text.encode('ascii', 'ignore')) for x in odd_w]
                file_odds_xy.append(odd_x)
                file_odds_xy_chain = list(itertools.chain.from_iterable(file_odds_xy))
                file_odds_xy_chain = ' '.join(file_odds_xy_chain)

            file_odds.append(file_odds_xy_chain)

        file_matchups = list(itertools.chain.from_iterable(file_matchups))

        browser.quit()

        game_df = pd.DataFrame(file_dates, columns=['Matchup_Date'])

        game_df['Matchup'] = file_matchups

        for date in game_df['Matchup_Date']:
            try:
                date = pd.to_datetime(date, format='%d/%m/%Y %H:%M')
            except ValueError:
                print "in-play game"
                continue

        game_df['Odds'] = file_odds
        game_df['Visitor_Odd'] = game_df["Odds"].str.split(' ').str.get(1)
        game_df['Home_Odd'] = game_df["Odds"].str.split(' ').str.get(0)
        game_df.drop('Odds', axis=1, inplace=True)

        True_Result = []
        string_to_check = "/"
        # For each row in the column,
        for row in game_df['Matchup_Date']:
            # if more than a value,
            if string_to_check in row:
                # Append a letter grade
                True_Result.append('Upcoming')

            else:
                # Append a failing grade
                True_Result.append('IN-PLAY')

        # Create a column from the list
        game_df['True_Result_U'] = True_Result

        # Drop potential matchups in in-play and dropping the Score column for simplicity
        game_df = game_df[game_df.True_Result_U != "IN-PLAY"]
        game_df.drop('True_Result_U', axis=1, inplace=True)

        # CHANGE 'HOURS' AND THE OPERATOR ACCORDING THE TIMEZONE FORMAT FOR MATCHUPS ON THE DATABASE SOURCE WEBSITE
        # eg: see timezone on basketball-reference
        game_df['Matchup_Date_GMT_Minus_4'] = game_df['Matchup_Date']
        game_df['Matchup_Date_GMT_Minus_4'] = pd.to_datetime(game_df['Matchup_Date_GMT_Minus_4'],
                                                             format='%d/%m/%Y %H:%M')
        game_df['Matchup_Date_GMT_Minus_4'] = game_df['Matchup_Date_GMT_Minus_4'] - timedelta(hours=4)
        game_df["Matchup_Date"] = game_df['Matchup_Date_GMT_Minus_4'].astype(str)
        game_df['Date'] = game_df["Matchup_Date"].str.split(' ').str.get(0)
        game_df['Date'] = pd.to_datetime(game_df['Date'], format='%Y/%m/%d')
        game_df['Time'] = game_df["Matchup_Date"].str.split(' ').str.get(1)
        game_df.drop('Matchup_Date', axis=1, inplace=True)
        game_df['Visitor_Team'] = game_df["Matchup"].str.split(' — ').str.get(1)
        game_df['Home_Team'] = game_df["Matchup"].str.split(' — ').str.get(0)
        game_df.drop('Matchup', axis=1, inplace=True)

        self.game_df = game_df

    # -------------------------------------------------------------------------------------------------------------------------------------

    def clean_data(self, game_df, league_name):
        # game_df['Visitor_Odd'] = game_df['Visitor_Odd'].str.lstrip('Away\n')
        # game_df['Home_Odd'] = game_df['Home_Odd'].str.lstrip('Home\n')
        game_df['Visitor_Odd'] = game_df['Visitor_Odd'].str.lstrip('(')
        game_df['Visitor_Odd'] = game_df['Visitor_Odd'].str.rstrip(')')
        game_df['Home_Odd'] = game_df['Home_Odd'].str.lstrip('(')
        game_df['Home_Odd'] = game_df['Home_Odd'].str.rstrip(')')

        game_df = game_df[game_df['Visitor_Odd'].notnull()]
        # game_df = game_df[game_df['Visitor_Team'].notnull()]
        # game_df = game_df[game_df['Home_Team'].notnull()]
        self.game_df1 = game_df
        game_df = game_df[game_df['Visitor_Odd'].str.contains('\n') == False]
        game_df = game_df[game_df['Home_Odd'].str.contains('\n') == False]

        game_df['Visitor_Odd'] = pd.to_numeric(game_df['Visitor_Odd'])
        game_df['Home_Odd'] = pd.to_numeric(game_df['Home_Odd'])

        game_df.insert(3, 'League', str(league_name))

        # Create a dictionary like in soccer model

        # for s, t in zip(db_team_names_list, team_names_list):
        # game_df['Visitor_Team'] = game_df['Visitor_Team'].str.strip().str.replace(t, s)
        # game_df['Home_Team'] = game_df['Home_Team'].str.strip().str.replace(t, s)

        self.game_df = game_df
        self.game_df2 = game_df

    # -------------------------------------------------------------------------------------------------------------------------------------

    def merge_with_tableau_output(self, game_df, tableau_filename, upcoming_games_output_filename_us,
                                  upcoming_games_output_filename_eu):

        left = pd.read_csv(tableau_filename)
        left['Visitor_Team'] = left['Visitor_Team']
        left['Home_Team'] = left['Home_Team']
        left['Date'] = pd.to_datetime(left['Date'], infer_datetime_format=True)
        self.left = left

        df = pd.merge(left, game_df, on=['Visitor_Team', 'Home_Team', 'Date'], how="inner")
        self.df = df
        df = df.sort_values(['Date', 'Time'])
        df['Sibyl'] = df.apply(lambda x: x['Home_Team'] if x['Predicted_Result'] == 1 else x['Visitor_Team'], axis=1)
        df['Bookies_choice'] = df.apply(
            lambda x: x['Home_Team'] if x['Home_Odd'] < x['Visitor_Odd'] else x['Visitor_Team'], axis=1)
        df['Divergence_Y/N'] = df[['Sibyl', 'Bookies_choice']].apply(lambda x: 'Y' if x[0] != x[1] else "N", axis=1)

        self.df1 = df
        df = df.drop('ID', axis=1)
        df = df.drop('V_Team_PTS', axis=1)
        df = df.drop('H_Team_PTS', axis=1)
        df['True_Result'] = 'Upcoming'

        self.df2 = df
        df['Confidence'] = df['Confidence'].round(3)
        df['Matchup_US_P'] = df['Visitor_Team'] + ' @ ' + df['Home_Team']
        df['Matchup_EU_P'] = df['Home_Team'] + ' vs ' + df['Visitor_Team']

        nba_us_p_df = pd.concat(
            [df['Date'], df['Time'], df['League'], df['Matchup_US_P'], df['Visitor_Team'], df['Home_Team'],
             df['Visitor_Odd'], df['Home_Odd'], df['Bookies_choice'], df['Sibyl'], df['Confidence'],
             df['Divergence_Y/N'],
             df['True_Result']], axis=1)

        nba_eu_p_df = pd.concat(
            [df['Date'], df['Time'], df['League'], df['Matchup_EU_P'], df['Home_Team'], df['Visitor_Team'],
             df['Home_Odd'], df['Visitor_Odd'], df['Bookies_choice'], df['Sibyl'], df['Confidence'],
             df['Divergence_Y/N'],
             df['True_Result']], axis=1)

        nba_us_p_df = nba_us_p_df.reset_index(drop=True)
        nba_eu_p_df = nba_eu_p_df.reset_index(drop=True)

        self.nba_us_p_df = nba_us_p_df
        self.nba_eu_p_df = nba_eu_p_df

        nba_us_p_df.to_csv(upcoming_games_output_filename_us, mode='w+', index=True, index_label='ID')
        nba_eu_p_df.to_csv(upcoming_games_output_filename_eu, mode='w+', index=True, index_label='ID')


if __name__ == '__main__':
    x = AcquireMatchupDatetimeOddsTwoChoices(
        'No', \
        "https://www.betbrain.com/basketball/united-states/nba/", \
        "nba_team_stats_2017_2017.csv", \
        "NBA", \
        "nba_tableau_output_2017.csv", \
        "NBA_Upcoming_Matchups_US_P_df.csv", \
        "NBA_Upcoming_Matchups_EU_P_df.csv")
    x()
