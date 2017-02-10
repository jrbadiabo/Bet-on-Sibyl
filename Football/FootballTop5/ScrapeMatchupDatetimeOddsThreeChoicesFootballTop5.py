# coding=utf-8
import itertools
from datetime import timedelta

import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait


def fix_str(s):
    s = s.strip()
    if ':' in s:
        if 'OT' in s:
            s = s[:s.find('OT')].strip()  # Used for basketball model
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


class AcquireMatchupDatetimeOddsThreeChoices(object):
    def __init__(self, betbrain_upcoming_games_url_template, cs_team_stats_filename, league_name, tableau_filename):
        self.betbrain_upcoming_games_url_template = betbrain_upcoming_games_url_template
        self.cs_team_stats_filename = cs_team_stats_filename
        self.league_name = league_name  # not used for the football
        self.tableau_filename = tableau_filename

    def __call__(self):
        self.generate_data(self.betbrain_upcoming_games_url_template)
        self.clean_data(self.game_df)
        self.merge_with_tableau_output(self.game_df, self.tableau_filename)

    # -------------------------------------------------------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------------------------------------------------------

    def generate_data(self, betbrain_upcoming_games_url_template):

        countries = ['germany', 'spain', 'italy', 'england', 'france']
        leagues = ['bundesliga', 'primera-division', 'serie-a', 'premier-league', 'ligue-1']
        all_matchups = []
        all_dates = []
        all_odds = []
        all_matchup_league = []
        delay = 5

        for country, league in zip(countries, leagues):
            url = betbrain_upcoming_games_url_template.format(country=country, league=league)

            try:
                browser = webdriver.Chrome("C:\Users\jbadiabo\PycharmProjects\Sibyl\chromedriver.exe")
                browser.set_page_load_timeout(20)
                while True:
                    try:
                        browser.get(url)
                    except TimeoutException:
                        print "Timeout, retrying..."
                        continue
                    else:
                        break
                WebDriverWait(browser, delay).until(ec.presence_of_element_located((By.CLASS_NAME, "MatchesList")))
                browser.quit()

                while True:
                    try:
                        browser = webdriver.Chrome("C:\Users\jbadiabo\PycharmProjects\Sibyl\chromedriver.exe")
                        browser.set_page_load_timeout(20)
                        while True:
                            try:
                                browser.get(url)
                            except TimeoutException:
                                print "Timeout, retrying..."
                                continue
                            else:
                                break
                        WebDriverWait(browser, delay).until(
                            ec.presence_of_element_located((By.CLASS_NAME, "MatchesList")))
                        table_check = browser.find_element_by_class_name("MatchesList")
                        body_rows_check = table_check.find_elements_by_class_name("Match")

                    except TimeoutException:
                        browser.quit()
                        delay += 3
                        continue
                    break

                browser.maximize_window()
                table = browser.find_element_by_class_name("MatchesList")
                body_rows = table.find_elements_by_class_name("Match")

                file_dates = []
                file_matchups = []
                file_odds = []
                matchup_league = []

                for row in body_rows:
                    date = row.find_element_by_class_name('DateTime')
                    date = [date.text.encode('utf-8')]
                    file_dates.extend(date)

                    matchup = row.find_element_by_class_name('MatchDetails')
                    matchup_d1 = matchup.find_element_by_class_name('MatchTitleLink')
                    matchup_d1 = [matchup_d1.text.encode('utf-8')]
                    file_matchups.extend(matchup_d1)

                    matchup_league.append(league)

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

                all_dates.extend(file_dates)
                all_matchups.extend(file_matchups)
                all_odds.extend(file_odds)
                all_matchup_league.extend(matchup_league)

                browser.quit()

            except TimeoutException:
                browser.quit()
                pass

        self.all_matchups = all_matchups
        self.all_dates = all_dates
        self.all_odds = all_odds
        self.all_matchup_league = all_matchup_league

        # -----------------------------------------------------------------------------------------------------------------------------------

        game_df = pd.DataFrame(all_dates, columns=['Matchup_Date'])

        game_df['League'] = all_matchup_league
        game_df['Matchup'] = all_matchups

        # To count the number of inplay game
        games_inplay = 0

        for date in game_df['Matchup_Date']:
            try:
                date = pd.to_datetime(date, format='%d/%m/%Y %H:%M')
            except ValueError:
                games_inplay += 1
                continue
        print "in-play games: " + str(games_inplay)

        game_df['Odds'] = all_odds
        game_df['Visitor_Odd'] = game_df["Odds"].str.split(' ').str.get(2)
        game_df['Draw_Odd'] = game_df["Odds"].str.split(' ').str.get(1)
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

        self.test_df2 = game_df

        # Create a column from the list
        game_df['True_Result_U'] = True_Result

        # Drop potential matchups in in-play and dropping the Score column for simplicity
        game_df = game_df[game_df.True_Result_U != "IN-PLAY"]
        game_df.drop('True_Result_U', axis=1, inplace=True)

        # CHANGE 'HOURS' AND THE OPERATOR ACCORDING THE TIMEZONE FORMAT FOR MATCHUPS ON THE DATABASE SOURCE WEBSITE
        # eg: see timezone on basketball-reference

        game_df['Matchup_Date_GMT_Plus_1'] = game_df['Matchup_Date']
        game_df['Matchup_Date_GMT_Plus_1'] = pd.to_datetime(game_df['Matchup_Date_GMT_Plus_1'], format='%d/%m/%Y %H:%M')
        game_df['Matchup_Date_GMT_Plus_1'] = game_df['Matchup_Date_GMT_Plus_1'] + timedelta(hours=1)
        game_df["Matchup_Date"] = game_df['Matchup_Date_GMT_Plus_1'].astype(str)
        game_df['Date'] = game_df["Matchup_Date"].str.split(' ').str.get(0)
        game_df['Date'] = pd.to_datetime(game_df['Date'], format='%Y/%m/%d')
        game_df['Time'] = game_df["Matchup_Date"].str.split(' ').str.get(1)
        game_df.drop('Matchup_Date', axis=1, inplace=True)
        # noinspection PyByteLiteral
        game_df['Visitor_Team'] = game_df["Matchup"].str.split(' — ').str.get(1)
        # noinspection PyByteLiteral
        game_df['Home_Team'] = game_df["Matchup"].str.split(' — ').str.get(0)
        game_df.drop('Matchup', axis=1, inplace=True)

        self.test_df1 = game_df
        self.game_df = game_df

    # -------------------------------------------------------------------------------------------------------------------------------------

    def clean_data(self, game_df):
        # game_df['Visitor_Odd'] = game_df['Visitor_Odd'].str.lstrip('Away\n')
        # game_df['Draw_Odd'] = game_df['Draw_Odd'].str.lstrip('Draw\n')
        # game_df['Home_Odd'] = game_df['Home_Odd'].str.lstrip('Home\n')
        game_df['Visitor_Odd'] = game_df['Visitor_Odd'].str.lstrip('(')
        game_df['Visitor_Odd'] = game_df['Visitor_Odd'].str.rstrip(')')
        game_df['Home_Odd'] = game_df['Home_Odd'].str.lstrip('(')
        game_df['Home_Odd'] = game_df['Home_Odd'].str.rstrip(')')
        game_df['Draw_Odd'] = game_df['Draw_Odd'].str.lstrip('(')
        game_df['Draw_Odd'] = game_df['Draw_Odd'].str.rstrip(')')

        self.test_df3 = game_df

        game_df = game_df[game_df['Visitor_Odd'].notnull()]
        game_df = game_df[game_df['Visitor_Team'].notnull()]
        game_df = game_df[game_df['Home_Team'].notnull()]
        game_df = game_df[game_df['Visitor_Odd'].str.contains('\n') == False]
        game_df = game_df[game_df['Draw_Odd'].str.contains('\n') == False]
        game_df = game_df[game_df['Home_Odd'].str.contains('\n') == False]

        self.test_df4 = game_df

        game_df['Visitor_Odd'] = pd.to_numeric(game_df['Visitor_Odd'])
        game_df['Draw_Odd'] = pd.to_numeric(game_df['Draw_Odd'])
        game_df['Home_Odd'] = pd.to_numeric(game_df['Home_Odd'])

        self.test_df5 = game_df

        # Taking the current season team stats df to take the list of teams
        team_name_dict = {'1. FC Koln': 'FC Koln', '1. FSV Mainz 05': 'FSV Mainz', 'AC Fiorentina': 'Fiorentina',
                          'AC Milan': 'AC Milan', 'AS Monaco': 'Monaco', 'AS Nancy Lorraine': 'Nancy',
                          'AS Roma': 'AS Roma', 'AS St. Etienne': 'Saint-Etienne', 'Alaves': 'Alaves',
                          'Angers SCO': 'Angers', 'Arsenal': 'Arsenal', 'Atalanta Bergamo': 'Atalanta',
                          'Athletic Bilbao': 'Athletic Bilbao', 'Atletico Madrid': 'Atletico Madrid',
                          'Bayer 04 Leverkusen': 'Leverkusen', 'Bologna F.C.': 'Bologna',
                          'Borussia Dortmund': 'Dortmund', 'Borussia Monchengladbach': 'Monchengladb.',
                          'Bournemouth AFC': 'Bournemouth', 'Burnley FC': 'Burnley', 'Cagliari': 'Cagliari',
                          'Celta de Vigo': 'Celta Vigo', 'Chelsea': 'Chelsea', 'Chievo Verona': 'Chievo',
                          'Crotone': 'Crotone', 'Crystal Palace FC': 'Crystal Palace',
                          'Deportivo La Coruna': 'Deportivo', 'Dijon FCO': 'Dijon', 'EA Guingamp': 'Guingamp',
                          'Eibar': 'Eibar', 'Eintracht Frankfurt': 'Frankfurt', 'Empoli': 'Empoli',
                          'Everton': 'Everton', 'FC Augsburg': 'Augsburg', 'FC Barcelona': 'FC Barcelona',
                          'FC Bayern Munchen': 'Bayern Munich', 'FC Girondins de Bordeaux': 'Bordeaux',
                          'FC Ingolstadt 04': 'Ingolstadt', 'FC Lorient': 'Lorient', 'FC Metz': 'Metz',
                          'FC Nantes': 'Nantes', 'FC Schalke 04': 'Schalke 04', 'FC Toulouse': 'Toulouse',
                          'Genoa': 'Genoa', 'Granada CF': 'Granada', 'Hamburger SV': 'Hamburger SV',
                          'Hertha BSC Berlin': 'Hertha Berlin', 'Hull City AFC': 'Hull City',
                          'Internazionale Milano': 'Inter Milan', 'Juventus FC': 'Juventus', 'Leganes': 'Leganes',
                          'Leicester City': 'Leicester City', 'Liverpool': 'Liverpool', 'Malaga CF': 'Malaga',
                          'Manchester City': 'Manchester City', 'Manchester United FC': 'Manchester Utd',
                          'Middlesbrough FC': 'Middlesbrough', 'Montpellier HSC': 'Montpellier', 'Napoli': 'Napoli',
                          'OGC Nice': 'Nice', 'OSC Lille': 'Lille', 'Olympique Lyonnais': 'Lyon',
                          'Olympique Marseille': 'Marseille', 'Osasuna': 'Osasuna', 'Palermo': 'Palermo',
                          'Paris Saint-Germain FC': 'Paris SG', 'Pescara': 'Pescara', 'RB Leipzig': 'RB Leipzig',
                          'RCD Espanyol': 'Espanyol', 'Real Betis': 'Real Betis', 'Real Madrid': 'Real Madrid',
                          'Real Sociedad': 'Real Sociedad', 'Real Sporting de Gijon': 'Sporting Gijon',
                          'SC Bastia': 'Bastia', 'SC Freiburg': 'Freiburg', 'SS Lazio': 'Lazio Roma',
                          'SV Darmstadt 98': 'Darmstadt', 'SV Werder Bremen': 'Werder Bremen', 'Sampdoria': 'Sampdoria',
                          'Sassuolo': 'Sassuolo', 'Sevilla FC': 'FC Sevilla', 'Southampton FC': 'Southampton',
                          'Stade Caen': 'Caen', 'Stade Rennes FC': 'Rennes', 'Stoke City FC': 'Stoke City',
                          'Sunderland': 'Sunderland', 'Swansea City': 'Swansea City',
                          'TSG 1899 Hoffenheim': 'Hoffenheim', 'Torino FC': 'Torino', 'Tottenham Hotspur': 'Tottenham',
                          'U.D. Las Palmas de Gran Canaria': 'Las Palmas', 'Udinese Calcio': 'Udinese',
                          'Valencia CF': 'Valencia', 'VfL Wolfsburg': 'Wolfsburg', 'Villarreal CF': 'Villarreal',
                          'Watford FC': 'Watford', 'West Bromwich Albion FC': 'West Bromwich',
                          'West Ham United': 'West Ham Utd'}

        for key, value in team_name_dict.iteritems():
            game_df.loc[game_df['Visitor_Team'] == key, 'Visitor_Team'] = value
            game_df.loc[game_df['Home_Team'] == key, 'Home_Team'] = value

        self.game_df = game_df

        self.team_name_dict = team_name_dict

    # -------------------------------------------------------------------------------------------------------------------------------------

    def merge_with_tableau_output(self, game_df, tableau_filename):

        left = pd.read_csv(tableau_filename)
        left['Date'] = pd.to_datetime(left['Date'], infer_datetime_format=True)
        self.left = left

        df = pd.merge(left, game_df, on=['Visitor_Team', 'Home_Team', 'Date'], how="inner")
        df = df.sort_values(['Date', 'Time'])
        df = df.reset_index(drop=True)
        df['Sibyl'] = df.apply(lambda x: x['Home_Team'] if x['Predicted_Result'] == 1 \
            else x['Visitor_Team'] if x['Predicted_Result'] == 2 else 'Draw', axis=1)
        df['Bookies_choice'] = df.apply(
            lambda x: x['Home_Team'] if x['Home_Odd'] < x['Visitor_Odd'] else x[
                'Visitor_Team'] if x['Visitor_Odd'] < x['Home_Odd'] else 'Draw', axis=1)
        df['Divergence_Y/N'] = df[['Sibyl', 'Bookies_choice']].apply(lambda x: 'Y' if x[0] != x[1] else "N", axis=1)

        df = df.drop('ID', axis=1)
        df = df.drop('V_Team_PTS', axis=1)
        df = df.drop('H_Team_PTS', axis=1)
        df['True_Result'] = 'Upcoming'

        df['Confidence'] = df['Confidence'].round(3)

        football_top5_us_p_df = pd.concat(
            [df['Date'], df['Time'], df['League'], df['Visitor_Team'], df['Home_Team'], df['Visitor_Odd'],
             df['Draw_Odd'],
             df['Home_Odd'], df['Bookies_choice'], df['Sibyl'], df['Confidence'], df['Divergence_Y/N'],
             df['True_Result']], axis=1)

        football_top5_eu_p_df = pd.concat(
            [df['Date'], df['Time'], df['League'], df['Home_Team'], df['Visitor_Team'], df['Home_Odd'], df['Draw_Odd'],
             df['Visitor_Odd'], df['Bookies_choice'], df['Sibyl'], df['Confidence'], df['Divergence_Y/N'],
             df['True_Result']], axis=1)

        football_top5_us_p_df = football_top5_us_p_df.sort_values(['League', 'Date', 'Time'])
        football_top5_eu_p_df = football_top5_eu_p_df.sort_values(['League', 'Date', 'Time'])

        football_top5_us_p_df = football_top5_us_p_df.reset_index(drop=True)
        football_top5_eu_p_df = football_top5_eu_p_df.reset_index(drop=True)

        for key, value in self.team_name_dict.iteritems():
            football_top5_us_p_df.loc[football_top5_us_p_df['Visitor_Team'] == value, 'Visitor_Team'] = key
            football_top5_us_p_df.loc[football_top5_us_p_df['Home_Team'] == value, 'Home_Team'] = key
            football_top5_us_p_df.loc[football_top5_us_p_df['Bookies_choice'] == value, 'Bookies_choice'] = key
            football_top5_us_p_df.loc[football_top5_us_p_df['Sibyl'] == value, 'Sibyl'] = key

        football_top5_us_p_df.insert(3, 'Matchup_US_P',
                                     football_top5_us_p_df['Visitor_Team'] + ' @ ' + football_top5_us_p_df['Home_Team'])

        football_top5_us_p_df = football_top5_us_p_df.loc[
            (football_top5_us_p_df['Home_Odd'] >= 1.) & (football_top5_us_p_df['Draw_Odd'] >= 1.) & (
                football_top5_us_p_df['Visitor_Odd'] >= 1.)]

        for key, value in self.team_name_dict.iteritems():
            football_top5_eu_p_df.loc[football_top5_eu_p_df['Visitor_Team'] == value, 'Visitor_Team'] = key
            football_top5_eu_p_df.loc[football_top5_eu_p_df['Home_Team'] == value, 'Home_Team'] = key
            football_top5_us_p_df.loc[football_top5_us_p_df['Bookies_choice'] == value, 'Bookies_choice'] = key
            football_top5_us_p_df.loc[football_top5_us_p_df['Sibyl'] == value, 'Sibyl'] = key

        football_top5_eu_p_df.insert(3, 'Matchup_US_P',
                                     football_top5_eu_p_df['Home_Team'] + ' vs ' + football_top5_eu_p_df[
                                         'Visitor_Team'])

        football_top5_eu_p_df = football_top5_eu_p_df.loc[
            (football_top5_eu_p_df['Home_Odd'] >= 1.) & (football_top5_eu_p_df['Draw_Odd'] >= 1.) & (
                football_top5_eu_p_df['Visitor_Odd'] >= 1.)]

        football_top5_us_p_df.to_csv('FootballTop5_Upcoming_Matchups_US_P_df.csv', mode='w+', index=True,
                                     index_label='ID')
        football_top5_eu_p_df.to_csv('FootballTop5_Upcoming_Matchups_EU_P_df.csv', mode='w+', index=True,
                                     index_label='ID')

        # -------------------------------------------------------------------------------------------------------------------------------------------------------
        # Creating a df for each league for level 2 pages

        bundesliga_eu_p_df = football_top5_eu_p_df.loc[football_top5_eu_p_df['League'] == 'bundesliga']
        bundesliga_us_p_df = football_top5_us_p_df.loc[football_top5_us_p_df['League'] == 'bundesliga']

        primera_division_eu_p_df = football_top5_eu_p_df.loc[football_top5_eu_p_df['League'] == 'primera-division']
        primera_division_us_p_df = football_top5_us_p_df.loc[football_top5_us_p_df['League'] == 'primera-division']

        serie_a_eu_p_df = football_top5_eu_p_df.loc[football_top5_eu_p_df['League'] == 'serie-a']
        serie_a_us_p_df = football_top5_us_p_df.loc[football_top5_us_p_df['League'] == 'serie-a']

        premier_league_eu_p_df = football_top5_eu_p_df.loc[football_top5_eu_p_df['League'] == 'premier-league']
        premier_league_us_p_df = football_top5_us_p_df.loc[football_top5_us_p_df['League'] == 'premier-league']

        ligue_1_eu_p_df = football_top5_eu_p_df.loc[football_top5_eu_p_df['League'] == 'ligue-1']
        ligue_1_us_p_df = football_top5_us_p_df.loc[football_top5_us_p_df['League'] == 'ligue-1']

        self.football_top5_eu_p_df = football_top5_eu_p_df
        self.bundesliga_eu_p_df = bundesliga_eu_p_df
        self.primera_division_eu_p_df = primera_division_eu_p_df
        self.serie_a_eu_p_df = serie_a_eu_p_df
        self.premier_league_eu_p_df = premier_league_eu_p_df
        self.ligue_1_eu_p_df = ligue_1_eu_p_df

        bundesliga_us_p_df.to_csv('Bundesliga_Upcoming_Matchups_US_P_df.csv', mode='w+', index=True, index_label='ID')
        bundesliga_eu_p_df.to_csv('Bundesliga_Upcoming_Matchups_EU_P_df.csv', mode='w+', index=True, index_label='ID')
        primera_division_us_p_df.to_csv('Primera_Division_Upcoming_Matchups_US_P_df.csv', mode='w+', index=True,
                                        index_label='ID')
        primera_division_eu_p_df.to_csv('Primera_Division_Upcoming_Matchups_EU_P_df.csv', mode='w+', index=True,
                                        index_label='ID')
        serie_a_us_p_df.to_csv('Serie_A_Upcoming_Matchups_US_P_df.csv', mode='w+', index=True, index_label='ID')
        serie_a_eu_p_df.to_csv('Serie_A_Upcoming_Matchups_EU_P_df.csv', mode='w+', index=True, index_label='ID')
        premier_league_us_p_df.to_csv('Premier_League_Upcoming_Matchups_US_P_df.csv', mode='w+', index=True,
                                      index_label='ID')
        premier_league_eu_p_df.to_csv('Premier_League_Upcoming_Matchups_EU_P_df.csv', mode='w+', index=True,
                                      index_label='ID')
        ligue_1_us_p_df.to_csv('Ligue_1_Upcoming_Matchups_US_P_df.csv', mode='w+', index=True, index_label='ID')
        ligue_1_eu_p_df.to_csv('Ligue_1_Upcoming_Matchups_EU_P_df.csv', mode='w+', index=True, index_label='ID')


if __name__ == '__main__':
    w = AcquireMatchupDatetimeOddsThreeChoices("https://www.betbrain.com/football/{country}/{league}/",
                                               'football_top5_team_stats_2017_2017.csv', 'FootballTop5',
                                               "football_top5_tableau_output_2017.csv")
    w()