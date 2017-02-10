# coding: utf-8

# In[60]:

import matplotlib.pyplot as plt
import pandas as pd
from bs4 import BeautifulSoup
from more_itertools import unique_everseen
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait


# get_ipython().magic(u'matplotlib inline')


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


class AcquireSibylVsBookiesNBA(object):
    def __init__(self, season_over, oddsportal_url_fix, oddsportal_url_list_format, cs_team_stats_filename,
                 tableau_input_filename):
        self.oddsportal_url_fix = oddsportal_url_fix
        self.oddsportal_url_list_format = oddsportal_url_list_format
        self.cs_team_stats_filename = cs_team_stats_filename
        self.tableau_input_filename = tableau_input_filename
        self.season_over = season_over

    def __call__(self):
        if self.season_over == 'No':
            print "Scraping the team names for compatibility with dbb names <= to be delete from us sports"
            self.get_team_names_list()
            print "OK"

            print "Finding the beginning of the season...."
            self.get_sea_beg_page(self.oddsportal_url_fix)
            print "OK"

            print "Scraping data..."
            self.generate_data(self.oddsportal_url_list_format, self.sea_beg_page)
            print "OK"

            print "Cleaning data..."
            self.clean_data(self.game_df, self.odd_tm_list, self.cs_team_stats_filename, self.tableau_input_filename)
            print "OK"

            print "Performing the simulation..."
            self.sibyl_vs_bookies_simulation(self.nba_us_p_df)
            print "OK"

        else:
            print "Season is over so we do not update Sibyl vs Bookies process"
            pass

    def fix_str(self):
        self = self.strip()
        if ':' in self:
            if 'OT' in self: self = self[:self.find('OT')].strip()  # Used for basketball model
            self = self.split(':')
            self = [int(_) for _ in self]
            self = [str(_) for _ in self]
            self = ' '.join(self)

        return self.encode('UTF-8')

    def get_team_names_list(self):

        browser = webdriver.Chrome("C:\Users\jbadiabo\PycharmProjects\Sibyl\chromedriver.exe")
        url = "http://www.oddsportal.com/basketball/usa/nba/outrights/"

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
                WebDriverWait(browser, delay).until(ec.presence_of_element_located((By.ID, "odds-data-table")))
            except TimeoutException:
                browser.quit()
                delay += 3
                continue
            break

        table = browser.find_element_by_id('odds-data-table')
        rows = table.find_elements_by_class_name('table-container')

        odd_tm_list = []
        for row in rows:
            link = row.find_element_by_tag_name('a')
            text = link.text.encode('utf8')
            odd_tm_list.append(text)

        odd_tm_list = sorted(odd_tm_list)
        self.odd_tm_list = odd_tm_list

        browser.quit()

    def get_sea_beg_page(self, oddsportal_url_fix):

        browser = webdriver.Chrome("C:\Users\jbadiabo\PycharmProjects\Sibyl\chromedriver.exe")

        delay = 5

        while True:
            try:
                browser.get(oddsportal_url_fix)
                WebDriverWait(browser, delay).until(ec.presence_of_element_located((By.LINK_TEXT, "»|")))
            except TimeoutException:
                browser.quit()
                delay += 3
                continue
            break

        last_page_link = browser.find_element_by_link_text('»|')
        last_page_link.click()

        right_page = False

        while not right_page:
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

            dates = browser.find_elements_by_xpath(".//th[@class='first2 tl']")

            dates = [element.text for element in dates]

            dates = dates[1:]

            dates = [x.encode('ascii', 'ignore') for x in dates]

            for date in dates:
                if 'Pre-season' in date:
                    one_back_page = browser.find_element_by_link_text('«')
                    try:
                        WebDriverWait(browser, delay).until(
                            ec.presence_of_element_located((By.XPATH, ".//a[2]/span[@class='arrow']")))
                    except TimeoutException as ex:
                        print ex.message
                    one_back_page.click()

                    break

                else:
                    right_page = True
            continue

        while True:
            try:
                browser.get(browser.current_url)
                WebDriverWait(browser, delay).until(ec.presence_of_element_located((By.CLASS_NAME, "active-page")))
            except TimeoutException:
                browser.quit()
                delay += 3
                continue
            break

        sea_beg_page = browser.find_element_by_class_name('active-page')
        sea_beg_page = int(sea_beg_page.text.encode('ascii', 'ignore'))
        self.sea_beg_page = sea_beg_page
        browser.quit()

    def generate_data(self, url_list_format, sea_beg_page):

        l_sea_beg_page = [sea_beg_page]

        url_list_format = [url_list_format]

        df = pd.DataFrame(columns=['Time', 'Matchup (reversed order - H/A)', 'Score', 'A_Odd', 'H_Odd'])

        l_date = []

        browser = webdriver.Chrome("C:\Users\jbadiabo\PycharmProjects\Sibyl\chromedriver.exe")

        if sea_beg_page == 1:
            end_page = 0
        else:
            end_page = 1

        for url, p in zip(url_list_format, l_sea_beg_page):
            for i in range(p, end_page, -1):

                delay = 5

                while True:
                    try:
                        browser.get(url.format(i))
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

                date = soup.find_all('span', {'class': 'datet'})
                date = [element.text for element in date]
                date = [x.encode('ascii', 'ignore') for x in date]

                times = soup.find_all('td', {'class': 'table-time'})
                times = [element.text for element in times]
                times = [x.encode('ascii', 'ignore') for x in times]

                h_odds = odds[::2]
                h_odds = [fix_odds(x) for x in h_odds]
                a_odds = odds[1::2]
                a_odds = [fix_odds(x) for x in a_odds]

                game_df = pd.DataFrame(times, columns=['Time'])
                game_df['Matchup (reversed order - H/A)'] = pd.Series(combined)
                game_df['Score'] = pd.Series(scores)
                game_df['A_Odd'] = pd.Series(a_odds)
                game_df['H_Odd'] = pd.Series(h_odds)
                game_df = game_df.fillna('')
                game_df = game_df[game_df.A_Odd != '']

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

        self.date = date
        self.df = df
        self.game_df = df

    def clean_data(self, game_df, odd_tm_list, cs_team_stats_filename, tableau_input_filename):

        game_df['A_Odd'] = pd.to_numeric(game_df['A_Odd'])
        game_df['H_Odd'] = pd.to_numeric(game_df['H_Odd'])

        game_df['Visitor_Team'] = game_df["Matchup (reversed order - H/A)"].str.split('-').str.get(1)
        game_df['Home_Team'] = game_df["Matchup (reversed order - H/A)"].str.split('-').str.get(0)
        game_df.drop('Matchup (reversed order - H/A)', axis=1, inplace=True)

        game_df['visi_team_pts'] = game_df["Score"].str.split(':').str.get(1)
        game_df['Home_Team_PTS'] = game_df["Score"].str.split(':').str.get(0)
        game_df.drop('Score', axis=1, inplace=True)

        # ----------------------------------------------------------------------------------------------------------------------------------

        # Taking the current season team stats df to take the list of teams
        current_sea_df = pd.read_csv(cs_team_stats_filename)
        db_tm_list = sorted(current_sea_df['Team'].tolist())

        # In your database
        suffixes = db_tm_list

        teams = odd_tm_list

        for s, t in zip(suffixes, teams):
            game_df['Visitor_Team'] = game_df['Visitor_Team'].str.strip().str.replace(t, s)
            game_df['Home_Team'] = game_df['Home_Team'].str.strip().str.replace(t, s)

            # ---------------------------------------------------------------------------------------------------------------------------------

        game_df['Visitor_Odd'] = game_df['A_Odd'].round(2)
        game_df['Home_Odd'] = game_df['H_Odd'].round(2)
        game_df.drop("A_Odd", axis=1, inplace=True)
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
        game_df = game_df[game_df.visi_team_pts != "postp."]
        game_df = game_df[game_df.visi_team_pts != "NaN."]

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
                matchup_day.append(self.date[0])
            else:
                matchup_day.append(self.date[1])
                self.date.pop(0)
        game_df['matchup_day'] = matchup_day
        game_df['matchup_day'] = game_df['matchup_day'].map(
            lambda x: x.lstrip('TomorrowToday,Yesterday,').rstrip(' 2016'))
        game_df['matchup_day'] = game_df['matchup_day'].map(lambda x: x.strip())
        game_df['matchup_day'] = game_df['matchup_day'].astype(str) + ' 2016'
        game_df['matchup_day'] = game_df['matchup_day'].replace(' ', '/', regex=True)
        game_df['Date'] = pd.to_datetime(game_df['matchup_day'], infer_datetime_format=True)
        game_df = game_df.drop('matchup_day', axis=1)
        game_df = game_df.drop('Hour_prev_m', axis=1)
        game_df = game_df.drop('Hour', axis=1)
        game_df = game_df.drop('Python_Times', axis=1)

        left = pd.read_csv(tableau_input_filename)
        left['Date'] = pd.to_datetime(left['Date'], infer_datetime_format=True)

        df = pd.merge(left, game_df, on=['Visitor_Team', 'Home_Team', 'Date'], how="inner")
        df = df.sort_values(['Date', 'Time'])
        df['Sibyl'] = df.apply(lambda x: x['Home_Team'] if x['Predicted_Result'] == 1 else x['Visitor_Team'], axis=1)
        df['Bookies_choice'] = df.apply(
            lambda x: x['Home_Team'] if x['Home_Odd'] < x['Visitor_Odd'] else x['Visitor_Team'], axis=1)
        df['Divergence_Y/N'] = df[['Sibyl', 'Bookies_choice']].apply(lambda x: 'Y' if x[0] != x[1] else "N", axis=1)

        df = df.drop('ID', axis=1)
        df = df.drop('V_Team_PTS', axis=1)
        df = df.drop('H_Team_PTS', axis=1)

        df['Confidence'] = df['Confidence'].round(3)
        df['Matchup_US_P'] = df['Visitor_Team'] + ' @ ' + df['Home_Team']
        df['Matchup_EU_P'] = df['Home_Team'] + ' vs ' + df['Visitor_Team']
        df['Winner_Odd'] = df.apply(
            lambda x: x['Visitor_Odd'] if x['True_Result'] == x['Visitor_Team'] else x['Home_Odd'], axis=1)

        nba_us_p_df = pd.concat(
            [df['Date'], df['Time'], df['Matchup_US_P'], df['Visitor_Team'], df['Home_Team'], df['Visitor_Odd'],
             df['Home_Odd'], df['Bookies_choice'], df['Sibyl'], df['Confidence'], df['Divergence_Y/N'],
             df['visi_team_pts'], df['Home_Team_PTS'], df['True_Result'], df['Winner_Odd']], axis=1)

        nba_us_p_df['True_Result'] = nba_us_p_df.apply(
            lambda x: x['Home_Team'] if x['True_Result'] == 1 else x['Visitor_Team'], axis=1)

        nba_eu_p_df = pd.concat(
            [df['Date'], df['Time'], df['Matchup_EU_P'], df['Home_Team'], df['Visitor_Team'], df['Home_Odd'],
             df['Visitor_Odd'], df['Bookies_choice'], df['Sibyl'], df['Confidence'], df['Divergence_Y/N'],
             df['Home_Team_PTS'], df['visi_team_pts'], df['True_Result'], df['Winner_Odd']], axis=1)

        nba_eu_p_df['True_Result'] = nba_us_p_df.apply(
            lambda x: x['Home_Team'] if x['True_Result'] == 1 else x['Visitor_Team'], axis=1)

        nba_us_p_df = nba_us_p_df.reset_index(drop=True)
        nba_eu_p_df = nba_eu_p_df.reset_index(drop=True)
        self.nba_us_p_df = nba_us_p_df
        self.nba_eu_p_df = nba_eu_p_df

        nba_us_p_df.to_csv('Sibyl_vs_Bookies_US_NBA.csv', mode='w+', index=True, index_label='ID')

        nba_eu_p_df.to_csv('Sibyl_vs_Bookies_EU_NBA.csv', mode='w+', index=True, index_label='ID')

    # Simple bettor, betting the same amount each time.

    def sibyl_vs_bookies_simulation(self, df):

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
        plt.plot(sibyl_balance, linewidth=3.0, linestyle='solid', color='yellow', label='Sibyl')
        plt.legend(loc='upper left')
        plt.plot(bookies_balance, linewidth=3.0, linestyle='solid', color='red', label='Bookies')
        plt.legend(loc='upper left')
        plt.title('Sibyl_vs_Bookies')
        plt.xlabel('N_Games')
        plt.ylabel('Balances')
        plt.grid(True)

        metrics = 'Sibyl ROI: ' + str(sibyl_roi) + '%' + '\n' + 'Sibyl Funds: ' + str(
            sibyl_value) + '\n' + 'Bookies ROI: ' + str(bookies_roi) + '%' + '\n' + 'Bookies Funds: ' + str(
            bookies_value) + '\n' + 'Number of games: ' + str(n_games)

        plt.text(-100, 0, metrics)
        plt.savefig('Sibyl_vs_Bookies_NBA.png', format='png')
        plt.close(fig)

        metrics_df = pd.DataFrame()
        metrics_df['sibyl_roi'] = [sibyl_roi]
        metrics_df['Sibyl_Funds'] = [sibyl_value]
        metrics_df['bookies_roi'] = [bookies_roi]
        metrics_df['Bookies_Funds'] = [bookies_value]
        metrics_df['N_Games'] = [n_games]

        self.metrics_df = metrics_df
        self.df = df

        metrics_df.to_csv('Sibyl_vs_Bookies_metrics_NBA.csv', mode='w+', index=True, index_label='ID')


if __name__ == '__main__':
    x = AcquireSibylVsBookiesNBA(
        'No', \
        "http://www.oddsportal.com/basketball/usa/nba/results/", \
        "http://www.oddsportal.com/basketball/usa/nba/results/#/page/{}/", \
        "nba_team_stats_2017_2017.csv", \
        "nba_tableau_output_2017.csv")
    x()
