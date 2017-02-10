# coding: utf-8

# In[101]:

import matplotlib.pyplot as plt
import pandas as pd
from bs4 import BeautifulSoup
from more_itertools import unique_everseen
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait


# get_ipython().magic(u'matplotlib inline')

def fix_str(s):
    s = s.strip()

    if ':' in s:
        for i in ['pen.', 'OT', 'award.']:
            if i in s:
                s = s.replace(i, "")
                s = s.strip()

    return s.encode('UTF-8')


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


class AcquireSibylVsBookiesFootballTop5(object):
    def __init__(self, oddsportal_url_fix_template, oddsportal_url_list_format_template, cs_team_stats_filename,
                 tableau_input_filename):
        self.oddsportal_url_fix_template = oddsportal_url_fix_template
        self.oddsportal_url_list_format_template = oddsportal_url_list_format_template
        self.cs_team_stats_filename = cs_team_stats_filename
        self.tableau_input_filename = tableau_input_filename

    def __call__(self):
        self.generate_data(self.oddsportal_url_fix_template)
        self.clean_data(self.game_df, self.tableau_input_filename)
        self.sibyl_vs_bookies_simulation(self.football_top5_us_p_df, self.leagues, self.football_top5_eu_p_df,
                                         self.bundesliga_eu_p_df, self.primera_division_eu_p_df, self.serie_a_eu_p_df,
                                         self.premier_league_eu_p_df, self.ligue_1_eu_p_df)

    def generate_data(self, oddsportal_url_fix_template):

        countries = ['germany', 'spain', 'italy', 'england', 'france']
        leagues = ['bundesliga', 'laliga', 'serie-a', 'premier-league', 'ligue-1']
        self.leagues = leagues  # We will use it again in a loop for plotting Sibyl vs the Bookies stats
        big_df = pd.DataFrame()
        all_dates = []

        for country, league in zip(countries, leagues):
            url = oddsportal_url_fix_template.format(country=country, league=league)
            browser = webdriver.Chrome("C:\Users\jbadiabo\PycharmProjects\Sibyl\chromedriver.exe")

            delay = 5

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
                    WebDriverWait(browser, delay).until(ec.presence_of_element_located((By.LINK_TEXT, "»|")))
                except TimeoutException:
                    browser.quit()
                    delay += 3
                    continue
                break

            last_page_link = browser.find_element_by_link_text('»|')
            last_page_link.click()

            while True:
                try:
                    browser.get(browser.current_url)
                    WebDriverWait(browser, delay).until(
                        ec.presence_of_element_located((By.XPATH, ".//th[@class='first2 tl']")))
                except TimeoutException:
                    browser.quit()
                    delay += 3
                    continue
                break

            sea_beg_page = browser.find_element_by_class_name('active-page')
            sea_beg_page = int(sea_beg_page.text.encode('ascii', 'ignore'))
            browser.quit()

            l_sea_beg_page = [sea_beg_page]

            oddsportal_url_list_format_template = [
                'http://www.oddsportal.com/soccer/{country}/{league}/results/#/page/{i}/']

            df = pd.DataFrame(
                columns=['League', 'Time', 'Matchup (reversed order - H/A)', 'Score', 'A_Odd', 'D_Odd', 'H_Odd'])

            l_date = []

            browser = webdriver.Chrome("C:\Users\jbadiabo\PycharmProjects\Sibyl\chromedriver.exe")

            if sea_beg_page == 1:
                end_page = 0
            else:
                end_page = 1

            for url, p in zip(oddsportal_url_list_format_template, l_sea_beg_page):
                for i in range(p, end_page, -1):

                    delay = 5

                    while True:
                        try:
                            browser.get(url.format(country=country, league=league, i=i))
                            WebDriverWait(browser, delay).until(
                                ec.presence_of_element_located((By.CLASS_NAME, "odds-nowrp")))
                        except TimeoutException:
                            browser.quit()
                            delay += 3
                            continue
                        break

                    odds = browser.find_elements_by_class_name('odds-nowrp')

                    html = browser.page_source
                    soup = BeautifulSoup(html, 'html5lib')

                    odds = [element.text for element in odds]
                    odds = [x.encode('ascii', 'ignore') for x in odds]
                    # Remove the last two elements of the list as there are empty
                    odds = odds[:-2]

                    data = soup.find_all('td', {'class': 'name table-participant'})

                    matchups = data
                    matchups = [element.text for element in matchups]

                    # Merge lists within the "matchups" list into one single list of multiple elements
                    combined = filter(None, matchups)
                    combined = [x for x in matchups if x.strip()]
                    combined = [x.encode('ascii', 'ignore') for x in matchups]

                    scores = soup.find_all('td', {'class': 'center bold table-odds table-score'})
                    scores = [element.text for element in scores]
                    scores = [x.encode('ascii', 'ignore') for x in scores]
                    scores = [fix_str(element) for element in scores]

                    date = soup.find_all('span', {'class': 'datet'})
                    date = [element.text for element in date]
                    date = [x.encode('ascii', 'ignore') for x in date]

                    times = soup.find_all('td', {'class': 'table-time'})
                    times = [element.text for element in times]
                    times = [x.encode('ascii', 'ignore') for x in times]

                    matchup_league = [league] * len(times)

                    h_odds = odds[::3]
                    h_odds = [fix_odds(x) for x in h_odds]
                    d_odds = odds[1::3]
                    d_odds = [fix_odds(x) for x in d_odds]
                    a_odds = odds[2::3]
                    a_odds = [fix_odds(x) for x in a_odds]

                    game_df = pd.DataFrame(matchup_league, columns=['League'])
                    game_df['Time'] = pd.Series(times)
                    game_df['Matchup (reversed order - H/A)'] = pd.Series(combined)
                    game_df['Score'] = pd.Series(scores)
                    game_df['A_Odd'] = pd.Series(a_odds)
                    game_df['D_Odd'] = pd.Series(d_odds)
                    game_df['H_Odd'] = pd.Series(h_odds)
                    game_df = game_df.fillna('')
                    game_df = game_df[game_df.A_Odd != '']
                    game_df = game_df[game_df.D_Odd != '']

                    game_df = game_df.iloc[::-1]

                    df = df.append(game_df, ignore_index=True)

                    date = date[::-1]
                    l_date.extend(date)
                    date = l_date
                    date = list(unique_everseen(date))
                    previous_page = browser.find_element_by_link_text('«')

                    try:
                        WebDriverWait(browser, delay).until(
                            ec.presence_of_element_located((By.XPATH, ".//a[2]/span[@class='arrow]")))
                    except TimeoutException:
                        pass

                    previous_page.click()

                browser.quit()

            big_df = big_df.append(df, ignore_index=True)
            all_dates.extend(date)

        self.date = date
        self.all_dates = all_dates
        self.df = df
        self.big_df = big_df
        self.game_df = big_df

    def clean_data(self, game_df, tableau_input_filename):

        game_df['A_Odd'] = pd.to_numeric(game_df['A_Odd'])
        game_df['D_Odd'] = pd.to_numeric(game_df['D_Odd'])
        game_df['H_Odd'] = pd.to_numeric(game_df['H_Odd'])

        game_df['Visitor_Team'] = game_df["Matchup (reversed order - H/A)"].str.split('-').str.get(1)
        game_df['Home_Team'] = game_df["Matchup (reversed order - H/A)"].str.split('-').str.get(0)
        game_df.drop('Matchup (reversed order - H/A)', axis=1, inplace=True)

        game_df['visi_team_pts'] = game_df["Score"].str.split(':').str.get(1)
        game_df['Home_Team_PTS'] = game_df["Score"].str.split(':').str.get(0)
        game_df.drop('Score', axis=1, inplace=True)

        game_df['Home_Team'] = game_df['Home_Team'].astype(str)
        game_df['Visitor_Team'] = game_df['Visitor_Team'].astype(str)

        # ----------------------------------------------------------------------------------------------------------------------------------

        # Taking the current season team stats df to take the list of teams
        team_name_dict = {'1. FC Koln': 'FC Koln', 'Mainz': '1. FSV Mainz', 'Fiorentina': 'Fiorentina',
                          'AC Milan': 'AC Milan', 'Monaco': 'Monaco', 'Nancy': 'Nancy', 'AS Roma': 'AS Roma',
                          'St Etienne': 'Saint-Etienne', 'Alaves': 'Alaves', 'Angers': 'Angers', 'Arsenal': 'Arsenal',
                          'Atalanta': 'Atalanta', 'Ath Bilbao': 'Athletic Bilbao', 'Atl. Madrid': 'Atletico Madrid',
                          'Bayer Leverkusen': 'Leverkusen', 'Bologna': 'Bologna', 'Dortmund': 'Dortmund',
                          'B. Monchengladbach': 'Monchengladb.', 'Bournemouth': 'Bournemouth', 'Burnley': 'Burnley',
                          'Cagliari': 'Cagliari', 'Celta Vigo': 'Celta Vigo', 'Chelsea': 'Chelsea', 'Chievo': 'Chievo',
                          'Crotone': 'Crotone', 'Crystal Palace': 'Crystal Palace', 'Dep. La Coruna': 'Deportivo',
                          'Dijon': 'Dijon', 'Guingamp': 'Guingamp', 'Eibar': 'Eibar',
                          'Eintracht Frankfurt': 'Frankfurt', 'Empoli': 'Empoli', 'Everton': 'Everton',
                          'FC Augsburg': 'Augsburg', 'Barcelona': 'FC Barcelona', 'Bayern Munich': 'Bayern Munich',
                          'Bordeaux': 'Bordeaux', 'Ingolstadt': 'Ingolstadt', 'Lorient': 'Lorient', 'Metz': 'Metz',
                          'Nantes': 'Nantes', 'Schalke': 'Schalke 04', 'Toulouse': 'Toulouse', 'Genoa': 'Genoa',
                          'Granada CF': 'Granada', 'Hamburger  SV': 'Hamburger SV', 'Hertha Berlin': 'Hertha Berlin',
                          'Hull City': 'Hull City', 'Inter': 'Inter Milan', 'Juventus': 'Juventus',
                          'Leganes': 'Leganes', 'Leicester': 'Leicester City', 'Liverpool': 'Liverpool',
                          'Malaga': 'Malaga', 'Manchester City': 'Manchester City',
                          'Manchester United': 'Manchester Utd', 'Middlesbrough': 'Middlesbrough',
                          'Montpellier': 'Montpellier', 'Napoli': 'Napoli', 'Nice': 'Nice', 'Lille': 'Lille',
                          'Lyon': 'Lyon', 'Marseille': 'Marseille', 'Osasuna': 'Osasuna', 'Palermo': 'Palermo',
                          'Paris SG': 'Paris SG', 'Pescara': 'Pescara', 'RB Leipzig': 'RB Leipzig',
                          'Espanyol': 'Espanyol', 'Betis': 'Real Betis', 'Real Madrid': 'Real Madrid',
                          'Real Sociedad': 'Real Sociedad', 'Gijon': 'Sporting Gijon', 'Bastia': 'Bastia',
                          'SC Freiburg': 'Freiburg', 'Lazio': 'Lazio Roma', 'Darmstadt': 'Darmstadt',
                          'SV Werder Bremen': 'Werder Bremen', 'Sampdoria': 'Sampdoria', 'Sassuolo': 'Sassuolo',
                          'Sevilla': 'FC Sevilla', 'Southampton': 'Southampton', 'Caen': 'Caen', 'Rennes': 'Rennes',
                          'Stoke City': 'Stoke City', 'Sunderland': 'Sunderland', 'Swansea': 'Swansea City',
                          'Hoffenheim': 'Hoffenheim', 'Torino': 'Torino', 'Tottenham': 'Tottenham',
                          'UD Las Palmas': 'Las Palmas', 'Udinese': 'Udinese', 'Valencia': 'Valencia',
                          'Wolfsburg': 'Wolfsburg', 'Villarreal': 'Villarreal', 'Watford': 'Watford',
                          'West Brom': 'West Bromwich', 'West Ham': 'West Ham Utd'}

        game_df['Visitor_Team'] = game_df['Visitor_Team'].str.strip()
        game_df['Home_Team'] = game_df['Home_Team'].str.strip()

        for key, value in team_name_dict.iteritems():
            game_df.loc[game_df['Visitor_Team'] == key, 'Visitor_Team'] = value
            game_df.loc[game_df['Home_Team'] == key, 'Home_Team'] = value

        self.team_name_dict = team_name_dict

        # ---------------------------------------------------------------------------------------------------------------------------------

        game_df['Visitor_Odd'] = game_df['A_Odd'].round(2)
        game_df['Draw_Odd'] = game_df['D_Odd'].round(2)
        game_df['Home_Odd'] = game_df['H_Odd'].round(2)
        game_df.drop("A_Odd", axis=1, inplace=True)
        game_df.drop("D_Odd", axis=1, inplace=True)
        game_df.drop("H_Odd", axis=1, inplace=True)

        True_Result = []
        string_to_check = ["'", 'Q', 'HT']
        # For each row in the column,
        for row in game_df['Time']:
            # if more than a value,
            if any(s in row for s in string_to_check):
                # Append a letter grade
                True_Result.append('IN-PLAY')

            else:
                # Append a failing grade
                True_Result.append('Upcoming')

        # Create a column from the list
        game_df['True_Result_U'] = True_Result

        # Drop potential matchups in in-play and dropping the Score column for simplicity
        game_df = game_df[game_df.True_Result_U != "IN-PLAY"]
        game_df.drop('True_Result_U', axis=1, inplace=True)

        game_df = game_df[game_df.Home_Team_PTS != "postp."]
        game_df = game_df[game_df.Home_Team_PTS != "NaN"]
        game_df = game_df[game_df.Home_Team_PTS != "award."]
        game_df = game_df[game_df.visi_team_pts != "postp."]
        game_df = game_df[game_df.visi_team_pts != "NaN."]
        game_df = game_df[game_df.visi_team_pts != "award."]

        # Adding a datetime column based on the values in 'Times' column
        game_df['Python_Times'] = pd.to_datetime(game_df['Time'], infer_datetime_format=True)
        # Adding a column based on the time of the previous game
        # to ease the comparison between and then enable the day shift
        game_df['Hour'] = game_df.Python_Times.apply(lambda x: x.hour)
        game_df['Hour_prev_m'] = game_df['Hour'].shift(1)
        game_df['Hour_prev_m'] = game_df['Hour_prev_m'].fillna(0)
        game_df['Hour_prev_m'] = game_df['Hour_prev_m'].astype('int')
        game_df['Hour'] = game_df['Hour'].astype('int')

        matchup_day = []

        for j, l in zip(game_df['Hour'], game_df['Hour_prev_m']):
            if j >= l:
                matchup_day.append(self.all_dates[0])
            else:
                matchup_day.append(self.all_dates[1])
                self.all_dates.pop(0)
        game_df['matchup_day'] = matchup_day
        game_df['matchup_day'] = game_df['matchup_day'].map(
            lambda x: x.lstrip('TomorrowToday,Yesterday,').rstrip(' 2017'))
        game_df['matchup_day'] = game_df['matchup_day'].map(lambda x: x.strip())
        game_df['matchup_day'] = game_df['matchup_day'].astype(str) + ' 2017'
        game_df['matchup_day'] = game_df['matchup_day'].replace(' ', '/', regex=True)
        game_df['Date'] = pd.to_datetime(game_df['matchup_day'], infer_datetime_format=True)
        game_df['Date'] = game_df['Date'].astype(str)
        game_df['date'], game_df['hour'] = game_df['Date'].str.split(' ', 1).str
        game_df['date'] = game_df['date'].str.strip()
        game_df = game_df.drop('Date', axis=1)
        game_df['Date'] = pd.to_datetime(game_df['date'], infer_datetime_format=True)
        game_df = game_df.drop('date', axis=1)
        game_df = game_df.drop('hour', axis=1)
        game_df = game_df.drop('matchup_day', axis=1)
        game_df = game_df.drop('Hour_prev_m', axis=1)
        game_df = game_df.drop('Hour', axis=1)
        game_df = game_df.drop('Python_Times', axis=1)

        left = pd.read_csv(tableau_input_filename)
        left['Date'] = pd.to_datetime(left['Date'], infer_datetime_format=True)

        # We retrieve the same "Date" condition as it is not well scraped
        df = pd.merge(left, game_df, on=['Visitor_Team', 'Home_Team'], how="inner")
        df = df.sort_values(['Date_x', 'Time'])
        df = df.drop('Date_y', axis=1)
        df['Date'] = df['Date_x']
        df = df.drop('Date_x', axis=1)

        df['Home_Team'] = df['Home_Team'].str.strip()
        df['Visitor_Team'] = df['Visitor_Team'].str.strip()

        df['Sibyl'] = df.apply(
            lambda x: x['Home_Team'] if x['Predicted_Result'] == 1 else x[
                'Visitor_Team'] if x['Predicted_Result'] == 2 else 'Draw' if x['Predicted_Result'] == 0 else None,
            axis=1)
        df['Bookies_choice'] = df.apply(
            lambda x: x['Home_Team'] if x['Home_Odd'] < x['Visitor_Odd'] else x[
                'Visitor_Team'] if x['Home_Odd'] > x['Visitor_Odd'] else 'Draw' if x['Home_Odd'] == x[
                'Visitor_Odd'] else None, axis=1)
        df['Divergence_Y/N'] = df[['Sibyl', 'Bookies_choice']].apply(
            lambda x: 'Y' if x[0] != x[1] else "N" if x[0] == x[1] else None, axis=1)

        df = df.drop('ID', axis=1)
        df = df.drop('V_Team_PTS', axis=1)
        df = df.drop('H_Team_PTS', axis=1)

        df['Confidence'] = df['Confidence'].round(3)
        df['Matchup_US_P'] = df['Visitor_Team'] + ' @ ' + df['Home_Team']
        df['Matchup_EU_P'] = df['Home_Team'] + ' vs ' + df['Visitor_Team']

        df['Bookies_choice'] = df['Bookies_choice'].str.strip()
        df['Sibyl'] = df['Sibyl'].str.strip()

        df['True_Result'] = df.apply(lambda x: x['Home_Team'] if x['True_Result'] == 1 else x['Visitor_Team'] if x[
                                                                                                                     'True_Result'] == 2 else 'Draw' if
        x['True_Result'] == 0 else None, axis=1)

        df['Winner_Odd'] = df.apply(
            lambda x: x['Visitor_Odd'] if x['True_Result'] == x['Visitor_Team'] else x['Home_Odd'] if x[
                                                                                                          'True_Result'] ==
                                                                                                      x[
                                                                                                          'Home_Team'] else
            x['Draw_Odd'] if x['True_Result'] == 'Draw' else None, axis=1)

        football_top5_us_p_df = pd.concat(
            [df['League'], df['Date'], df['Time'], df['Matchup_US_P'], df['Visitor_Team'], df['Home_Team'],
             df['Visitor_Odd'], df['Draw_Odd'], df['Home_Odd'], df['Bookies_choice'], df['Sibyl'], df['Confidence'],
             df['Divergence_Y/N'], df['visi_team_pts'], df['Home_Team_PTS'], df['True_Result'], df['Winner_Odd']],
            axis=1)

        football_top5_eu_p_df = pd.concat(
            [df['League'], df['Date'], df['Time'], df['Matchup_EU_P'], df['Home_Team'], df['Visitor_Team'],
             df['Home_Odd'], df['Draw_Odd'], df['Visitor_Odd'], df['Bookies_choice'], df['Sibyl'], df['Confidence'],
             df['Divergence_Y/N'], df['Home_Team_PTS'], df['visi_team_pts'], df['True_Result'], df['Winner_Odd']],
            axis=1)

        football_top5_us_p_df = football_top5_us_p_df.reset_index(drop=True)
        football_top5_eu_p_df = football_top5_eu_p_df.reset_index(drop=True)

        football_top5_us_p_df.to_csv('Sibyl_vs_Bookies_US_FootballTop5.csv', mode='w+', index=True, index_label='ID')

        football_top5_eu_p_df.to_csv('Sibyl_vs_Bookies_EU_FootballTop5.csv', mode='w+', index=True, index_label='ID')

        # -------------------------------------------------------------------------------------------------------------------------------------------------------
        # Creating a df for each league for level 2 pages

        bundesliga_eu_p_df = football_top5_eu_p_df.loc[football_top5_eu_p_df['League'] == 'bundesliga']
        bundesliga_us_p_df = football_top5_us_p_df.loc[football_top5_us_p_df['League'] == 'bundesliga']

        primera_division_eu_p_df = football_top5_eu_p_df.loc[football_top5_eu_p_df['League'] == 'laliga']
        primera_division_us_p_df = football_top5_us_p_df.loc[football_top5_us_p_df['League'] == 'laliga']

        serie_a_eu_p_df = football_top5_eu_p_df.loc[football_top5_eu_p_df['League'] == 'serie-a']
        serie_a_us_p_df = football_top5_us_p_df.loc[football_top5_us_p_df['League'] == 'serie-a']

        premier_league_eu_p_df = football_top5_eu_p_df.loc[football_top5_eu_p_df['League'] == 'premier-league']
        premier_league_us_p_df = football_top5_us_p_df.loc[football_top5_us_p_df['League'] == 'premier-league']

        ligue_1_eu_p_df = football_top5_eu_p_df.loc[football_top5_eu_p_df['League'] == 'ligue-1']
        ligue_1_us_p_df = football_top5_us_p_df.loc[football_top5_us_p_df['League'] == 'ligue-1']

        self.game_df = game_df
        self.left = left
        self.df = df

        self.football_top5_us_p_df = football_top5_us_p_df
        self.football_top5_eu_p_df = football_top5_eu_p_df
        self.bundesliga_eu_p_df = bundesliga_eu_p_df
        self.primera_division_eu_p_df = primera_division_eu_p_df
        self.serie_a_eu_p_df = serie_a_eu_p_df
        self.premier_league_eu_p_df = premier_league_eu_p_df
        self.ligue_1_eu_p_df = ligue_1_eu_p_df

        bundesliga_us_p_df.to_csv('Sibyl_vs_Bookies_US_Bundesliga.csv', mode='w+', index=True, index_label='ID')
        bundesliga_eu_p_df.to_csv('Sibyl_vs_Bookies_EU_Bundesliga.csv', mode='w+', index=True, index_label='ID')
        primera_division_us_p_df.to_csv('Sibyl_vs_Bookies_US_Primera_Division.csv', mode='w+', index=True,
                                        index_label='ID')
        primera_division_eu_p_df.to_csv('Sibyl_vs_Bookies_EU_Primera_Division.csv', mode='w+', index=True,
                                        index_label='ID')
        serie_a_us_p_df.to_csv('Sibyl_vs_Bookies_US_Serie_A.csv', mode='w+', index=True, index_label='ID')
        serie_a_eu_p_df.to_csv('Sibyl_vs_Bookies_EU_Serie_A.csv', mode='w+', index=True, index_label='ID')
        premier_league_us_p_df.to_csv('Sibyl_vs_Bookies_US_Premier_League.csv', mode='w+', index=True, index_label='ID')
        premier_league_eu_p_df.to_csv('Sibyl_vs_Bookies_EU_Premier_League.csv', mode='w+', index=True, index_label='ID')
        ligue_1_us_p_df.to_csv('Sibyl_vs_Bookies_US_Ligue_1.csv', mode='w+', index=True, index_label='ID')
        ligue_1_eu_p_df.to_csv('Sibyl_vs_Bookies_EU_Ligue_1', mode='w+', index=True, index_label='ID')

    def sibyl_vs_bookies_simulation(self, df, leagues, football_top5_eu_p_df, bundesliga_eu_p_df,
                                    primera_division_eu_p_df, serie_a_eu_p_df, premier_league_eu_p_df, ligue_1_eu_p_df):
        dfs = [football_top5_eu_p_df, bundesliga_eu_p_df, primera_division_eu_p_df, serie_a_eu_p_df,
               premier_league_eu_p_df, ligue_1_eu_p_df]

        for df, league in zip(dfs, leagues):

            n_games = len(df.index)

            sibyl_value = 1000
            bookies_value = 1000
            wager = 100

            sibyl_balance = []
            bookies_balance = []

            # -----------------------Sibyl----------------------------------------
            for i, row in df.iterrows():
                if row['Sibyl'] == row['True_Result']:
                    sibyl_value += (wager * row['Winner_Odd']) - wager
                    sibyl_balance.append(sibyl_value)
                else:
                    sibyl_value -= wager
                    sibyl_balance.append(sibyl_value)

            df['sibyl_balance'] = sibyl_balance

            # ----------------------Bookies---------------------------------------

            for i, row in df.iterrows():
                if row['Bookies_choice'] == row['True_Result']:
                    bookies_value += (wager * row['Winner_Odd']) - wager
                    bookies_balance.append(bookies_value)
                else:
                    bookies_value -= wager
                    bookies_balance.append(bookies_value)

            df['bookies_balance'] = bookies_balance

            # ----------------------Metrics---------------------------------------

            sibyl_roi = ((sibyl_value - 1000) / 1000) * 100

            bookies_roi = ((bookies_value - 1000) / 1000) * 100

            # ----------------------Plotting---------------------------------------

            fig = plt.figure()
            # fig2, ax = plt.subplots()
            plt.plot(sibyl_balance, linewidth=3.0, linestyle='solid', color='yellow', label='Sibyl')
            plt.legend(loc='upper left')
            plt.plot(bookies_balance, linewidth=3.0, linestyle='solid', color='red', label='Bookies')
            plt.legend(loc='upper left')
            plt.title('Sibyl_vs_Bookies_' + league)
            plt.xlabel('N_Games')
            plt.ylabel('Balances')
            plt.grid(True)

            metrics = 'Sibyl ROI: ' + str(sibyl_roi) + '%' + '\n' + 'Sibyl Funds: ' + str(
                sibyl_value) + '\n' + 'Bookies ROI: ' + str(bookies_roi) + '%' + '\n' + 'Bookies Funds: ' + str(
                bookies_value) + '\n' + 'Number of games: ' + str(n_games)

            # Below code not used so far
            # Now let's add your additional information
            # ax.annotate(metrics, xy=(0.5, 0), xytext=(0, -20), xycoords=('axes fraction', 'figure fraction'),\
            # textcoords='offset points', size=10, ha='center', va='bottom')

            plt.savefig('Sibyl_vs_Bookies_' + league + '.png', format='png')
            plt.close(fig)
            # plt.close(ax)

            metrics_df = pd.DataFrame()
            metrics_df['sibyl_roi'] = [sibyl_roi]
            metrics_df['Sibyl_Funds'] = [sibyl_value]
            metrics_df['bookies_roi'] = [bookies_roi]
            metrics_df['Bookies_Funds'] = [bookies_value]
            metrics_df['N_Games'] = [n_games]

            metrics_df.to_csv('Sibyl_vs_Bookies_metrics_' + league + '.csv', mode='w+', index=True, index_label='ID')

            # ex of use
            # x = AcquireSibylVsBookiesFootballTop5("http://www.oddsportal.com/soccer/{country}/{league}/results/",\
            # "http://www.oddsportal.com/soccer/{country}/{league}/results/#/page/{i}/",\
            # "football_top5_team_stats_2017_2017.csv",\
            # "football_top5_tableau_output_2017.csv")
