# coding: utf-8
import itertools
from datetime import timedelta
import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait


def fix_str(s):
    s = s.strip()
    if ':' in s:
        if 'OT' in s: s = s[:s.find('OT')].strip()  # Used for am-football model
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


class AcquireBetBrainATPUpcomingGames(object):
    def __init__(self):
        self.betbrain_url = "https://www.betbrain.com/tennis/"
        self.league_name = "ATP"

    def __call__(self):

        delay = 5
        while True:
            browser = webdriver.Chrome("C:\Users\jbadiabo\PycharmProjects\Sibyl\chromedriver.exe")
            try:
                browser.set_page_load_timeout(15)
                browser.get(self.betbrain_url)
                browser.maximize_window()
                WebDriverWait(browser, delay).until(ec.presence_of_element_located((By.CLASS_NAME, "PopularCountries")))

            except TimeoutException:
                browser.quit()
                delay += 3
                continue

            break

        popular_countries_div = browser.find_element_by_class_name("PopularCountries")
        popular_countries_list = popular_countries_div.find_element_by_tag_name("ul")
        popular_countries_list_elements = popular_countries_list.find_elements_by_tag_name("li")
        popular_countries_list_element_urls = [x.find_element_by_tag_name("a").get_attribute("href") for x in
                                               popular_countries_list_elements]

        all_countries_div = browser.find_element_by_class_name("AllCountries")
        all_countries_list = all_countries_div.find_element_by_tag_name("ul")
        all_countries_list_elements = all_countries_list.find_elements_by_tag_name("li")
        all_countries_list_element_urls = [x.find_element_by_tag_name("a").get_attribute("href") for x in
                                           all_countries_list_elements]

        popular_countries_list_element_urls += all_countries_list_element_urls

        browser.quit()

        big_df = pd.DataFrame()

        for popular_countries_list_element_url in popular_countries_list_element_urls:
            while True:

                try:
                    browser = webdriver.Chrome("C:\Users\jbadiabo\PycharmProjects\Sibyl\chromedriver.exe")
                    browser.set_page_load_timeout(15)
                    browser.get(popular_countries_list_element_url)
                    browser.maximize_window()
                    WebDriverWait(browser, delay).until(
                        ec.presence_of_element_located((By.CSS_SELECTOR, "ol.itemLeftMenu.Active")))

                except TimeoutException:
                    browser.quit()
                    delay += 3
                    continue

                break

            left_menu = browser.find_element_by_css_selector("ol.itemLeftMenu.Active")
            left_menu_elements = left_menu.find_elements_by_tag_name("li")
            tournament_buttons = [x for x in left_menu_elements if
                                  ("ATP" in x.text or "Open" in x.text or "Davis" in x.text) and
                                  (not "Challenger" in x.text or not "Doubles" in x.text or not "Women" in x.text\
                                  or not "Juniors" in x.text or not "Boys" in x.text or not "Girls" in x.text)]

            string_to_avoid = ["Challenger", "Doubles", "Women", "Juniors", "Boys", "Girls"]
            tournament_buttons = [x for x in tournament_buttons if not any(s in x.text for s in string_to_avoid)]
            tournament_button_urls = [x.find_element_by_css_selector("a.SelectLink") for x in tournament_buttons]
            tournament_button_urls = tournament_button_urls[0::2]

            country_url = browser.current_url
            browser.quit()

            for i in range(len(tournament_button_urls)):

                while True:

                    try:
                        browser = webdriver.Chrome("C:\Users\jbadiabo\PycharmProjects\Sibyl\chromedriver.exe")
                        browser.set_page_load_timeout(15)
                        browser.get(country_url)
                        browser.maximize_window()
                        WebDriverWait(browser, delay).until(
                            ec.presence_of_element_located((By.CSS_SELECTOR, "ol.itemLeftMenu.Active")))

                    except TimeoutException:
                        browser.quit()
                        delay += 3
                        continue

                    break

                left_menu = browser.find_element_by_css_selector("ol.itemLeftMenu.Active")
                left_menu_elements = left_menu.find_elements_by_tag_name("li")
                tournament_buttons = [x for x in left_menu_elements if
                                      ("ATP" in x.text or "Open" in x.text or "Davis" in x.text) \
                                      and not "Challenger" in x.text and not "Doubles" in x.text and not "Women" in x.text]
                tournament_button_urls = [x.find_element_by_css_selector("a.SelectLink") for x in tournament_buttons]
                tournament_button_url = tournament_button_urls[i]
                tournament_button_url.click()
                browser.implicitly_wait(3)  # seconds
                browser.get(browser.current_url)
                print browser.current_url

                # Checking if there is matchups in this league
                # If not this block of code will raise exception and we will pass this script
                try:
                    table_check = browser.find_element_by_class_name("MatchesList")
                except NoSuchElementException:
                    browser.quit()
                    continue

                # Give unicode string => to use it use str() or encode("ascii", "ignore")
                while True:
                    try:
                        WebDriverWait(browser, 10).until(ec.presence_of_element_located((By.CLASS_NAME, "MatchesList")))
                        tournament_name = browser.find_element_by_css_selector("h1.LeagueTitle").text
                    except TimeoutException:
                        continue
                    else:
                        break

                body_rows = table_check.find_elements_by_class_name("Match")

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

                # -----------------------------------------------------------------

                game_df = pd.DataFrame(file_dates, columns=['Matchup_Date'])

                game_df['Matchup'] = file_matchups

                # To count the number of inplay game
                games_inplay = 0

                for date in game_df['Matchup_Date']:
                    try:
                        date = pd.to_datetime(date, format='%d/%m/%Y %H:%M')
                    except ValueError:
                        games_inplay += 1
                        continue
                print "in-play games: " + str(games_inplay)

                game_df['Odds'] = file_odds
                game_df['Player_A_Odd'] = game_df["Odds"].str.split(' ').str.get(0)
                game_df['Player_B_Odd'] = game_df["Odds"].str.split(' ').str.get(1)
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
                # eg: see timezone on am-football-reference

                game_df['Matchup_Date_GMT_Plus_1'] = game_df['Matchup_Date']
                game_df['Matchup_Date_GMT_Plus_1'] = pd.to_datetime(game_df['Matchup_Date_GMT_Plus_1'],
                                                                    format='%d/%m/%Y %H:%M')
                game_df['Matchup_Date_GMT_Plus_1'] = game_df['Matchup_Date_GMT_Plus_1'] + timedelta(hours=1)
                game_df["Matchup_Date"] = game_df['Matchup_Date_GMT_Plus_1'].astype(str)
                game_df['Date'] = game_df["Matchup_Date"].str.split(' ').str.get(0)
                game_df['Date'] = pd.to_datetime(game_df['Date'], format='%Y/%m/%d')
                game_df['Time'] = game_df["Matchup_Date"].str.split(' ').str.get(1)
                game_df.drop('Matchup_Date', axis=1, inplace=True)
                game_df['Player_A'] = game_df["Matchup"].str.split(' — ').str.get(0)
                game_df['Player_B'] = game_df["Matchup"].str.split(' — ').str.get(1)
                game_df.drop('Matchup', axis=1, inplace=True)

                # ---------------------------------------------------------------

                # game_df['Visitor_Odd'] = game_df['Visitor_Odd'].str.lstrip('Away\n')
                # game_df['Home_Odd'] = game_df['Home_Odd'].str.lstrip('Home\n')
                game_df['Player_A_Odd'] = game_df['Player_A_Odd'].str.lstrip('(')
                game_df['Player_A_Odd'] = game_df['Player_A_Odd'].str.rstrip(')')
                game_df['Player_B_Odd'] = game_df['Player_B_Odd'].str.lstrip('(')
                game_df['Player_B_Odd'] = game_df['Player_B_Odd'].str.rstrip(')')

                game_df = game_df[game_df['Player_A_Odd'].notnull()]
                # game_df = game_df[game_df['Visitor_Team'].notnull()]
                # game_df = game_df[game_df['Home_Team'].notnull()]
                game_df = game_df[game_df['Player_A_Odd'].str.contains('\n') == False]
                game_df = game_df[game_df['Player_B_Odd'].str.contains('\n') == False]

                game_df['Player_A_Odd'] = pd.to_numeric(game_df['Player_A_Odd'])
                game_df['Player_B_Odd'] = pd.to_numeric(game_df['Player_B_Odd'])

                # -to remove when implementing for real
                game_df.insert(3, 'League', self.league_name)
                game_df.insert(4, 'Tournament', str(tournament_name))
                game_df.insert(6, 'Year', game_df['Date'].map(lambda x: x.year))
                game_df.insert(9, 'True_Result', 'W')

                browser.quit()

                big_df = big_df.append(game_df)
                big_df = big_df.drop_duplicates()
                self.big_df = big_df

                subset_df = pd.concat(
                    [big_df['Year'], big_df['Date'], big_df['Player_A'], big_df['Player_B'], big_df['True_Result']],
                    axis=1)
                subset_df['Player_A'] = subset_df['Player_A'].str.replace('-', ' ')
                subset_df['Player_B'] = subset_df['Player_B'].str.replace('-', ' ')
                subset_df.to_csv("atp_game_stats_current_season_from_betbrain_.csv", index=False, mode='w+')
