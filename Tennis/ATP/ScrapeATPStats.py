# coding: utf8
import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
import unicodedata
from multiprocessing import Process
import datetime
import sys
import csv


# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------Class Definition--------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------

class ScrapeATPStats(object):
    from AcquireBetBrainATPUpcomingGames import AcquireBetBrainATPUpcomingGames

    # ------------------------------------------------------------------------------------------------------------------
    # ----------------------------------------Init & Call---------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------

    def __init__(self, split_list, for_current_season):
        self.split_list = split_list
        self.players_game_data = []
        self.players_stat_data = []
        self.for_current_season = for_current_season
        self.current_datetime = datetime.datetime.now()
        # We will start scraping current season stats for predictions from March
        self.beginning_month_to_scrape_current_season_stats = 3

    def __call__(self):
        # Scraping both stat and game data of the players within the range
        print "Scraping data from " + str(self.split_list[0]) + " to " + str(self.split_list[-1])
        for self.i in self.split_list:
            self.go_on_atp_ranking_page()
            self.go_on_player_profile_page(self.browser)
            self.go_on_player_statistics_page(self.browser)
            self.scrape_player_stat_data(self.browser, self.players_stat_data,
                                         self.for_current_season, self.current_datetime,
                                         self.beginning_month_to_scrape_current_season_stats)
            self.go_on_player_game_data_page(self.browser)
            self.scrape_player_game_data(self.browser, self.players_game_data, self.for_current_season)
            print "---Next player---"

        # One the data scraped and put in proper format we convert it to csv file
        print "---Done---\n"
        self.data_to_csv(self.players_stat_data, self.players_game_data, self.split_list, self.for_current_season,
                         self.player_list)

    """
        if self.for_current_season == "Yes":
            print "---Scraping upco games from betbrain for merging---"
            j = self.AcquireBetBrainATPUpcomingGames()
            j()
            self.merge_with_bb_upco_games_for_current_year(self.players_game_data_df, self.split_list)
            print "---Done---\n"
        else:
            print "---Done---\n"
                                """

    # ------------------------------------------------------------------------------------------------------------------
    # ---------------------------------------Class Functions------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------

    # --- Going on the core tennis website ---
    def go_on_atp_ranking_page(self):
        url = "http://www.coretennis.net/"
        delay = 60  # seconds

        while True:
            browser = webdriver.Chrome("C:\Users\jbadiabo\PycharmProjects\Sibyl\chromedriver.exe")
            browser.set_page_load_timeout(delay)
            try:
                browser.get(url)
                # ---Going on the ATP Ranking page---
                browser.maximize_window()

                try:
                    atp_ranking_button = browser.find_element_by_xpath(".//div[@class='menu1']/a[4]")
                    atp_ranking_url = atp_ranking_button.get_attribute("href")
                except NoSuchElementException:
                    atp_ranking_button = browser.find_element_by_partial_link_text("Tennis Rankings")
                    atp_ranking_url = atp_ranking_button.get_attribute("href")

                atp_ranking_button.click()
                browser.get(browser.current_url)
                print "opening: " + atp_ranking_url
                browser.get(atp_ranking_url)

            except TimeoutException:
                print "Timeout on atp ranking page, retrying"
                browser.quit()
                continue
            else:
                break

        self.browser = browser

    # ------------------------------------------------------------------------------------------------------------------

    def go_on_player_profile_page(self, browser):
        # ---Going on player profile---
        current_url = browser.current_url
        delay = 60

        # ---------------- Getting player list for later checking the game df--------------
        player_list_first_half = browser.find_elements_by_xpath("//tbody/tr[@class='rrow1']/td[2]/a[@class='link']")
        player_list_second_half = browser.find_elements_by_xpath("//tbody/tr[@class='rrow2']/td[2]/a[@class='link']")
        player_list = player_list_first_half + player_list_second_half
        with open('player_list.csv', 'wb') as myfile:
            wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
            wr.writerow(player_list)

        self.player_list = player_list
        # ---------------------------------------------------------------------------------

        try:
            try:
                table = browser.find_element_by_id('rtable2')
            except NoSuchElementException:
                table = browser.find_elements_by_tag_name("table")[0]

            body = table.find_element_by_tag_name('tbody')
            table_rows = body.find_elements_by_tag_name('tr')
            table_rows = table_rows[1:]
            player_name_cell = table_rows[self.i].find_elements_by_tag_name('td')[1]
            player_profile_link = player_name_cell.find_element_by_tag_name('a')
            player_profile_url = player_profile_link.get_attribute('href')
            player_profile_link.click()
            browser.get(browser.current_url)
        except TimeoutException:
            while True:
                try:
                    print "Timeout opening player page, retrying, should open player profile page.."
                    browser.quit()
                    browser = webdriver.Chrome("C:\Users\jbadiabo\PycharmProjects\Sibyl\chromedriver.exe")
                    delay += 10
                    browser.set_page_load_timeout(delay)
                    print "opening: " + player_profile_url
                    browser.get(player_profile_url)
                    browser.maximize_window()
                except TimeoutException:
                    print "Timeout on recreeating the driver, retrying.."
                    continue
                else:
                    break

        self.browser = browser

    # ------------------------------------------------------------------------------------------------------------------

    # ---Going on player statistics profile---
    def go_on_player_statistics_page(self, browser):
        current_url = browser.current_url
        delay = 60

        try:
            try:
                player_statistics_link = browser.find_element_by_link_text("Statistics")
                player_statistics_url = player_statistics_link.get_attribute('href')
            except NoSuchElementException:
                player_statistics_link = browser.find_element_by_xpath(".//div[@class='ppNav']/a[4]")
                player_statistics_url = player_statistics_link.get_attribute('href')

            player_statistics_link.click()
            browser.get(browser.current_url)
        except TimeoutException:
            while True:
                try:
                    print "Timeout going on stats page, retrying, should open player stat profile.."
                    browser.quit()
                    browser = webdriver.Chrome("C:\Users\jbadiabo\PycharmProjects\Sibyl\chromedriver.exe")
                    delay += 10
                    browser.set_page_load_timeout(delay)
                    print "opening: " + player_statistics_url
                    browser.get(player_statistics_url)
                    browser.maximize_window()
                except TimeoutException:
                    continue
                else:
                    break

        self.browser = browser

    # ------------------------------------------------------------------------------------------------------------------

    # ---Scraping player stats---
    def scrape_player_stat_data(self, browser, players_stat_data, for_current_season, current_datetime,
                                beginning_month_to_scrape_current_season_stats):
        main_div = browser.find_element_by_id("colMainContent1b")

        player_name_header = main_div.find_element_by_class_name("ppHeader")
        player_name = player_name_header.find_element_by_tag_name('h1').text.encode("ascii", "ignore")

        player_name = player_name.rsplit(' ', 2)[0]  # 2 for 2nd split starting from the right

        table_titles = main_div.find_elements_by_tag_name("h2")
        table_titles = [x.text.encode('ascii', 'ignore') for x in table_titles]
        stat_tables = main_div.find_elements_by_class_name("sTable")
        number_of_years = len(stat_tables)

        year_player_data = []

        if for_current_season == 'No':  # Mostly used for training, we take all season stat data

            for stat_table, table_title in zip(stat_tables, table_titles):

                try:
                    year = table_title.split(" ")[0]
                    # ------------------------------------------------------------------------------------
                    table_footer = stat_table.find_element_by_tag_name("tfoot")
                    table_footer_row = table_footer.find_element_by_tag_name("tr")
                    data = [player_name, year]
                    table_footer_row_data = table_footer_row.find_elements_by_tag_name("td")

                    for i in table_footer_row_data:
                        data.append(i.text.encode('ascii', 'ignore'))

                    year_player_data.append(data)
                except NoSuchElementException:
                    continue

        else:  # Meaning for_current_season == 'Yes'
            # Then we have 2 cases:

            if current_datetime.month >= beginning_month_to_scrape_current_season_stats:  # Post March: Then we scrape current season data for predictions

                for stat_table, table_title in zip(stat_tables, table_titles):

                    try:
                        year = table_title.split(" ")[0]
                        if year == str(current_datetime.year):
                            # ------------------------------------------------------------------------------------
                            table_footer = stat_table.find_element_by_tag_name("tfoot")
                            table_footer_row = table_footer.find_element_by_tag_name("tr")
                            data = [player_name, year]
                            table_footer_row_data = table_footer_row.find_elements_by_tag_name("td")

                            for i in table_footer_row_data:
                                data.append(i.text.encode('ascii', 'ignore'))

                            year_player_data.append(data)
                        else:
                            continue

                    except NoSuchElementException:
                        continue
            # Ante March: Then we scrape data of the previous season (ex: 2016) for the current_season_predictions
            else:

                for stat_table, table_title in zip(stat_tables, table_titles):

                    try:
                        year = table_title.split(" ")[0]
                        if year == str(current_datetime.year - 1):
                            # ------------------------------------------------------------------------------------
                            table_footer = stat_table.find_element_by_tag_name("tfoot")
                            table_footer_row = table_footer.find_element_by_tag_name("tr")
                            year = int(year) + 1
                            year = str(year)
                            data = [player_name, year]  # We fake there are stats for current season until we
                            # have enough data to so => until March
                            table_footer_row_data = table_footer_row.find_elements_by_tag_name("td")

                            for i in table_footer_row_data:
                                data.append(i.text.encode('ascii', 'ignore'))

                            year_player_data.append(data)
                        else:
                            continue

                    except NoSuchElementException:
                        continue

        players_stat_data += year_player_data

        self.players_stat_data = players_stat_data

        self.browser = browser

    # ------------------------------------------------------------------------------------------------------------------

    # ---Going on the player game data---
    def go_on_player_game_data_page(self, browser):
        delay = 60
        try:
            main_div = browser.find_element_by_id("colMainContent1b")
            nav_div = main_div.find_element_by_class_name("ppNav")

            try:
                results_button = nav_div.find_element_by_partial_link_text("Results")
                results_url = results_button.get_attribute("href")
            except NoSuchElementException:
                results_button = nav_div.find_element_by_xpath(".//div[@class='ppNav']/a[3]")
                results_url = results_button.get_attribute("href")

            results_button.click()
            browser.get(browser.current_url)
        except TimeoutException:
            while True:
                try:
                    print "Timeout going on game stat page, retrying, should open player game stat data page.."
                    browser.quit()
                    browser = webdriver.Chrome("C:\Users\jbadiabo\PycharmProjects\Sibyl\chromedriver.exe")
                    delay += 10
                    browser.set_page_load_timeout(delay)
                    print "opening: " + results_url
                    browser.get(results_url)
                    browser.maximize_window()
                except TimeoutException:
                    continue
                else:
                    break

        self.browser = browser

    # ------------------------------------------------------------------------------------------------------------------

    # ---Scraping player game_data---
    def scrape_player_game_data(self, browser, players_game_data, for_current_season):
        player_game_data = []

        year_nav_div = browser.find_element_by_class_name("shadetabs")
        year_button_links = year_nav_div.find_elements_by_tag_name("li")

        main_div = browser.find_element_by_class_name("tabcontentstyle")
        year_divs = main_div.find_elements_by_class_name("tabcontent")

        if for_current_season == 'No':  # Mostly used for training, we take all season stat data

            for year_button_link, year_div in zip(year_button_links, year_divs):
                year_button_link.click()

                # --- Scraping the year ---
                year = year_nav_div.find_element_by_css_selector("li.selected").text.encode("ascii", "ignore")

                # ---Scraping player name---
                header = browser.find_element_by_class_name("ppHeader")
                player_name = header.find_element_by_css_selector('h1').text.encode("ascii", "ignore")
                player_name = player_name.rsplit(' ', 2)[0]  # 2 for 2nd split starting from the right

                # ---Scraping game data---
                containers = year_div.find_elements_by_class_name("pprContainer")
                year_container_rows_data = []

                for container in containers:

                    container_datetime_range = container.find_element_by_css_selector("div.pprHead")
                    try:
                        container_datetime_range = container_datetime_range.find_elements_by_tag_name("div")[
                            0].text.encode("ascii", "ignore")
                    except NoSuchElementException:
                        container_datetime_range = container_datetime_range.find_element_by_class_name("plM1")

                    container_datetime_range = container_datetime_range.replace("\n", " - ")

                    container_rows = container.find_elements_by_css_selector("div.pprRow")

                    container_rows_data = []
                    for row in container_rows:
                        data = row.find_elements_by_tag_name("div")
                        data = [x.text.encode("ascii", "ignore") for x in data]

                        indices = 0, 2, 4
                        data = [i for j, i in enumerate(data) if j not in indices]
                        data.insert(0, data.pop(1))
                        data.insert(0, player_name)
                        data.insert(0, container_datetime_range)
                        data.insert(0, year)

                        container_rows_data.append(data)

                    year_container_rows_data = year_container_rows_data + container_rows_data

                player_game_data = player_game_data + year_container_rows_data

        else:  # Meaning for_current_season == 'Yes'

            year_button_links[0].click()

            # --- Scraping the year ---
            year = year_nav_div.find_element_by_css_selector("li.selected").text.encode("ascii", "ignore")

            # ---Scraping player name---
            header = browser.find_element_by_class_name("ppHeader")
            player_name = header.find_element_by_css_selector('h1').text.encode("ascii", "ignore")
            player_name = player_name.rsplit(' ', 2)[0]  # 2 for 2nd split starting from the right

            # ---Scraping game data---
            containers = year_divs[0].find_elements_by_class_name("pprContainer")
            year_container_rows_data = []

            for container in containers:

                container_datetime_range = container.find_element_by_css_selector("div.pprHead")
                try:
                    container_datetime_range = container_datetime_range.find_elements_by_tag_name("div")[
                        0].text.encode("ascii", "ignore")
                except NoSuchElementException:
                    container_datetime_range = container_datetime_range.find_element_by_class_name("plM1")

                container_datetime_range = container_datetime_range.replace("\n", " - ")

                container_rows = container.find_elements_by_css_selector("div.pprRow")

                container_rows_data = []
                for row in container_rows:
                    data = row.find_elements_by_tag_name("div")
                    data = [x.text.encode("ascii", "ignore") for x in data]

                    indices = 0, 2, 4
                    data = [i for j, i in enumerate(data) if j not in indices]
                    data.insert(0, data.pop(1))
                    data.insert(0, player_name)
                    data.insert(0, container_datetime_range)
                    data.insert(0, year)

                    container_rows_data.append(data)

                year_container_rows_data = year_container_rows_data + container_rows_data

            player_game_data = player_game_data + year_container_rows_data

        players_game_data = players_game_data + player_game_data

        self.players_game_data = players_game_data

        browser.quit()

    # ------------------------------------------------------------------------------------------------------------------

    def data_to_csv(self, players_stat_data, players_game_data, split_list, for_current_season, player_list):

        players_stat_data_df = pd.DataFrame(players_stat_data,
                                            columns=['Player_name', 'Year', 'Tourn', 'Titles', 'Matches', 'Wins',
                                                     'Losses', 'PCT', '6-0', '0-6', '7-6', '6-7'])
        players_stat_data_df['Player_name'] = players_stat_data_df['Player_name'].str.rstrip().str.lstrip().str.replace(
            '-', ' ')
        if for_current_season == "No":
            players_stat_data_df = players_stat_data_df[players_stat_data_df.Year != "2017"]
        else:
            pass
        players_stat_data_df = players_stat_data_df.sort_values(['Year'])

        # ------------------------------------------------------------

        players_game_data_df = pd.DataFrame(players_game_data,
                                            columns=['Year', 'Date', 'Player_A', 'Player_B', 'True_Result'])
        players_game_data_df['Player_B'] = players_game_data_df['Player_B'].str[:-5]
        players_game_data_df.insert(1, 'Start', players_game_data_df['Date'].str.split(' - ').str.get(0))
        players_game_data_df.drop('Date', axis=1, inplace=True)
        players_game_data_df.insert(1, 'Date', players_game_data_df['Year'] + ',' + players_game_data_df['Start'])
        players_game_data_df.drop('Start', axis=1, inplace=True)
        players_game_data_df['Date'] = players_game_data_df['Date'].str.replace(' ', ',')
        players_game_data_df['Date'] = pd.to_datetime(players_game_data_df['Date'], infer_datetime_format=True)
        players_game_data_df['Player_A'] = players_game_data_df['Player_A'].str.rstrip().str.lstrip().str.replace('-',
                                                                                                                  ' ')
        players_game_data_df['Player_B'] = players_game_data_df['Player_B'].str.rstrip().str.lstrip().str.replace('-',
                                                                                                                  ' ')

        # Dropping duplicate rows
        players_game_data_df['Winner'] = players_game_data_df.apply(
            lambda x: x['Player_A'] if x['True_Result'] == 'W' else x['Player_B'], axis=1)
        players_game_data_df['Looser'] = players_game_data_df.apply(
            lambda x: x['Player_A'] if x['True_Result'] == 'L' else x['Player_B'], axis=1)
        players_game_data_df.drop_duplicates(subset=['Date', 'Winner', 'Looser'], inplace=True)
        players_game_data_df.drop(['Winner', 'Looser'], axis=1, inplace=True)

        # Dropping rows that do not involve 2 ATP players cuz we do not have data on no-ATP players.

        players_game_data_df = players_game_data_df[players_game_data_df.Player_A.isin(player_list)]
        players_game_data_df = players_game_data_df[players_game_data_df.Player_B.isin(player_list)]

        # -----------------------------------------------------------------------
        if for_current_season == "No":
            players_game_data_df = players_game_data_df[players_game_data_df.Year != "2017"]
        else:
            pass

        players_game_data_df = players_game_data_df.sort_values(['Year', 'Date'])

        # -----------------------------------------------------
        if for_current_season == "No":
            players_stat_data_df.to_csv("atp_player_stats_until_" + str(split_list[-1]) + "_.csv", mode='w+')
            self.players_stat_data_df = players_stat_data_df

            """
            players_game_data_df['Date'].to_csv("date_atp_game_stats.csv", mode='w+', header=False, index=False)
            players_game_data_df.drop('Date', axis=1, inplace=True)
            """

            players_game_data_df.to_csv("atp_game_stats_until_" + str(split_list[-1]) + "_.csv", index=False, mode='w+')
            self.players_game_data_df = players_game_data_df

            # for current season we only send to csv stat data
        else:
            players_stat_data_df.to_csv("atp_player_stats_until_" + str(split_list[-1]) + "_current_season.csv",
                                        mode='w+')

            self.players_game_data_df = pd.concat(
                [players_game_data_df['Year'], players_game_data_df['Date'], players_game_data_df['Player_A'],
                 players_game_data_df['Player_B'], players_game_data_df['True_Result']],
                axis=1)
            players_game_data_df.to_csv("atp_game_stats_until_" + str(split_list[-1]) + "_current_season.csv",
                                        index=False, mode='w+')


# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------Class Definition--------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------


# Scrape Tennis data split by split for ATP players
class ScrapingATPSplitBySplit(object):
    from AcquireBetBrainATPUpcomingGames import AcquireBetBrainATPUpcomingGames

    # ------------------------------------------------------------------------------------------------------------------
    # ----------------------------------------Init & Call---------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------

    # Initialisation for the current season or not
    def __init__(self, for_current_season):
        self.for_current_season = for_current_season

    def __call__(self):
        # First for performance efficiency we divide the ATP players in 10 parts
        # Then we group the splits in 2 main parts
        # We run each of the 2 parts one at the time
        # Each element within one part is a function, so for ex: in one part we run 5 function simultaneously
        self.run_in_parallel((self.scraping_split_one, self.for_current_season),
                             (self.scraping_split_two, self.for_current_season),
                             (self.scraping_split_three, self.for_current_season),
                             (self.scraping_split_four, self.for_current_season),
                             (self.scraping_split_five, self.for_current_season))

        self.run_in_parallel((self.scraping_split_six, self.for_current_season),
                             (self.scraping_split_seven, self.for_current_season),
                             (self.scraping_split_eight, self.for_current_season),
                             (self.scraping_split_nine, self.for_current_season),
                             (self.scraping_split_ten, self.for_current_season))

        # Now we have 20 (10 x 2 (stat, game)) dfs in csv files
        # We merge them into 2 big dfs, for game and stat data
        # There are different operations based on whether or not we init for current season
        self.merge_game_and_stat_dfs_from_splits(self.for_current_season)

        if self.for_current_season == "Yes":
            # For the current season, we upcoming game data from betbrain so that later we can perform prediction on it
            print "---Scraping upco games from betbrain for merging---"
            j = self.AcquireBetBrainATPUpcomingGames()
            j()
            # Then we merge both training game data and upcoming (unseen) game data into one df => to csv
            self.merge_with_bb_upco_games_for_current_year(self.game_df, self.stat_df)
            print "---Done---\n"
        else:
            self.training_game_data_to_csv(self.game_df, self.stat_df)
            print "---Scraping Training Data Done---\n"

    # ------------------------------------------------------------------------------------------------------------------
    # ----------------------------------------Class functions-----------------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------

    def merge_game_and_stat_dfs_from_splits(self, for_current_season):

        # We take different files based on whether or not we init to scrape the current season
        if for_current_season == "Yes":

            game_df_10 = pd.read_csv("atp_game_stats_until_10_current_season.csv")
            game_df_20 = pd.read_csv("atp_game_stats_until_20_current_season.csv")
            game_df_30 = pd.read_csv("atp_game_stats_until_30_current_season.csv")
            game_df_40 = pd.read_csv("atp_game_stats_until_40_current_season.csv")
            game_df_50 = pd.read_csv("atp_game_stats_until_50_current_season.csv")
            game_df_60 = pd.read_csv("atp_game_stats_until_60_current_season.csv")
            game_df_70 = pd.read_csv("atp_game_stats_until_70_current_season.csv")
            game_df_80 = pd.read_csv("atp_game_stats_until_80_current_season.csv")
            game_df_90 = pd.read_csv("atp_game_stats_until_90_current_season.csv")
            game_df_99 = pd.read_csv("atp_game_stats_until_99_current_season.csv")

        else:

            game_df_10 = pd.read_csv("atp_game_stats_until_10_.csv")
            game_df_20 = pd.read_csv("atp_game_stats_until_20_.csv")
            game_df_30 = pd.read_csv("atp_game_stats_until_30_.csv")
            game_df_40 = pd.read_csv("atp_game_stats_until_40_.csv")
            game_df_50 = pd.read_csv("atp_game_stats_until_50_.csv")
            game_df_60 = pd.read_csv("atp_game_stats_until_60_.csv")
            game_df_70 = pd.read_csv("atp_game_stats_until_70_.csv")
            game_df_80 = pd.read_csv("atp_game_stats_until_80_.csv")
            game_df_90 = pd.read_csv("atp_game_stats_until_90_.csv")
            game_df_99 = pd.read_csv("atp_game_stats_until_99_.csv")

        # We merge all the splits into one list...
        frames = [game_df_10, game_df_20, game_df_30, game_df_40, game_df_50, game_df_60, game_df_70,
                  game_df_80,
                  game_df_90, game_df_99]

        # ... that we then convert to a dataframe
        game_df = pd.concat(frames)
        self.game_df = game_df

        # ----------------------------------Merge Stat dfs----------------------------------------------------------

        # We take different files based on whether or not we init to scrape the current season
        if for_current_season == "Yes":

            stat_df_10 = pd.read_csv("atp_player_stats_until_10_current_season.csv")
            stat_df_20 = pd.read_csv("atp_player_stats_until_20_current_season.csv")
            stat_df_30 = pd.read_csv("atp_player_stats_until_30_current_season.csv")
            stat_df_40 = pd.read_csv("atp_player_stats_until_40_current_season.csv")
            stat_df_50 = pd.read_csv("atp_player_stats_until_50_current_season.csv")
            stat_df_60 = pd.read_csv("atp_player_stats_until_60_current_season.csv")
            stat_df_70 = pd.read_csv("atp_player_stats_until_70_current_season.csv")
            stat_df_80 = pd.read_csv("atp_player_stats_until_80_current_season.csv")
            stat_df_90 = pd.read_csv("atp_player_stats_until_90_current_season.csv")
            stat_df_99 = pd.read_csv("atp_player_stats_until_99_current_season.csv")

        else:

            stat_df_10 = pd.read_csv("atp_player_stats_until_10_.csv")
            stat_df_20 = pd.read_csv("atp_player_stats_until_20_.csv")
            stat_df_30 = pd.read_csv("atp_player_stats_until_30_.csv")
            stat_df_40 = pd.read_csv("atp_player_stats_until_40_.csv")
            stat_df_50 = pd.read_csv("atp_player_stats_until_50_.csv")
            stat_df_60 = pd.read_csv("atp_player_stats_until_60_.csv")
            stat_df_70 = pd.read_csv("atp_player_stats_until_70_.csv")
            stat_df_80 = pd.read_csv("atp_player_stats_until_80_.csv")
            stat_df_90 = pd.read_csv("atp_player_stats_until_90_.csv")
            stat_df_99 = pd.read_csv("atp_player_stats_until_99_.csv")

        # We merge all the splits into one list...
        frames = [stat_df_10, stat_df_20, stat_df_30, stat_df_40, stat_df_50, stat_df_60, stat_df_70,
                  stat_df_80,
                  stat_df_90, stat_df_99]

        # ... that we then convert to a dataframe
        stat_df = pd.concat(frames)

        self.stat_df = stat_df

    # ------------------------------------------------------------------------------------------------------------------

    def merge_with_bb_upco_games_for_current_year(self, game_df, stat_df):

        # Merging both training and upcoming game data into one df
        subset_df = pd.read_csv("atp_game_stats_current_season_from_betbrain_.csv")
        frames = [game_df, subset_df]
        players_game_data_df = pd.concat(frames)
        players_game_data_df = pd.DataFrame(players_game_data_df)
        players_game_data_df = players_game_data_df[players_game_data_df.Player_B != ""]
        players_game_data_df = players_game_data_df[players_game_data_df.Player_B != "NaN"]

        players_game_data_df['Date'].to_csv("date_atp_game_stats_current_season.csv", mode='w+', header=False,
                                            index=False)

        players_game_data_df.drop('Date', axis=1, inplace=True)

        players_game_data_df.to_csv("atp_game_stats_current_season.csv",
                                    index=False, mode='w+')

        # ------------------Stat df To Csv---------------------------

        stat_df = pd.DataFrame(stat_df)
        stat_df.drop(stat_df.columns[0], axis=1, inplace=True)
        stat_df = stat_df.reset_index(drop=True)
        stat_df.to_csv("atp_player_stats_current_season.csv", mode='w+')

    # ------------------------------------------------------------------------------------------------------------------

    def training_game_data_to_csv(self, game_df, stat_df):

        game_df = pd.DataFrame(game_df)

        game_df = game_df[game_df.Player_B != ""]
        game_df = game_df[game_df.Player_B != "NaN"]

        game_df['Date'].to_csv("date_atp_game_stats_training.csv", mode='w+', header=False,
                               index=False)

        game_df.drop('Date', axis=1, inplace=True)

        game_df.to_csv("atp_game_stats_training.csv",
                       index=False, mode='w+')

        # Check the below line
        stat_df = pd.DataFrame(stat_df)
        stat_df.drop(stat_df.columns[0], axis=1, inplace=True)
        stat_df = stat_df.reset_index(drop=True)
        stat_df.to_csv("atp_player_stats_training.csv", mode='w+')

    # ------------------------------------------------------------------------------------------------------------------

    # Defining functions for Scraping ATP data split by split
    # For each split we run the ScrapeATPStats which scrape game and stat data for the 10 players within that part
    # The init of the ScrapeATPStats is what range of players we take and the if we perform scraping for the current
    # season or not
    def scraping_split_one(self, for_current_season):
        a = ScrapeATPStats(range(10, 11), for_current_season)  # 11
        a()

    def scraping_split_two(self, for_current_season):
        b = ScrapeATPStats(range(20, 21), for_current_season)  # 11, 21
        b()

    def scraping_split_three(self, for_current_season):
        c = ScrapeATPStats(range(30, 31), for_current_season)  # 21, 31
        c()

    def scraping_split_four(self, for_current_season):
        d = ScrapeATPStats(range(40, 41), for_current_season)  # 31, 41 and so on...
        d()

    def scraping_split_five(self, for_current_season):
        e = ScrapeATPStats(range(50, 51), for_current_season)
        e()

    def scraping_split_six(self, for_current_season):
        f = ScrapeATPStats(range(60, 61), for_current_season)
        f()

    def scraping_split_seven(self, for_current_season):
        g = ScrapeATPStats(range(70, 71), for_current_season)
        g()

    def scraping_split_eight(self, for_current_season):
        h = ScrapeATPStats(range(80, 81), for_current_season)
        h()

    def scraping_split_nine(self, for_current_season):
        i = ScrapeATPStats(range(90, 91), for_current_season)
        i()

    def scraping_split_ten(self, for_current_season):
        j = ScrapeATPStats(range(99, 100), for_current_season)
        j()

    def run_in_parallel(self, *fns):
        proc = []
        for fn, arg in fns:
            p = Process(target=fn, args=(arg,))
            p.start()
            proc.append(p)
        for p in proc:
            p.join()


# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------IF MAIN-----------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    # __init__: for_current_season
    x = ScrapingATPSplitBySplit(sys.argv[1])
    x()
