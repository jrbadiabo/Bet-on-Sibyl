# coding: utf-8

import unicodedata
import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import TimeoutException


class AcquireFootballTop5TeamStats(object):
    def __init__(self, year1, year2):
        self.year1 = year1
        self.year2 = year2

    def __call__(self):
        # ---------------------------OFF STATS---------------------------------
        self.get_football_top5_team_stats(self.year1, self.year2)
        self.clean_data(self.team_df)

    def get_football_top5_team_stats(self, year1, year2):

        countries = ['germany', 'spain', 'italy', 'england', 'france']

        url_template = "http://www.soccerstats.com/latest.asp?league={country}_{year}"
        url_template_cs = "http://www.soccerstats.com/latest.asp?league={country}"

        team_df = pd.DataFrame()

        for country in countries:

            for year in range(year1, year2 + 1):

                browser = webdriver.Chrome("C:\Users\jbadiabo\PycharmProjects\Sibyl\chromedriver.exe")

                file_data = []
                if year == 2017:
                    url = url_template_cs.format(country=country)
                else:
                    url = url_template.format(country=country, year=year)

                browser.set_page_load_timeout(20)
                while True:
                    try:
                        browser.get(url)
                    except TimeoutException:
                        print "Timeout, retrying..."
                        continue
                    else:
                        break

                if year == 2017:
                    tables = browser.find_elements_by_id('btable')
                    table = tables[2]
                else:
                    table = browser.find_element_by_id('btable')

                body = table.find_element_by_tag_name('tbody')

                body_rows = body.find_elements_by_tag_name('tr')

                for row in body_rows:
                    data = row.find_elements_by_tag_name('td')

                    file_row = []
                    for datum in data:
                        try:
                            datum = datum.text.encode('utf8')
                            datum = datum.decode('utf8')
                            datum = unicodedata.normalize('NFD', datum).encode('ascii', 'ignore')
                            file_row.append(datum)
                        except:
                            file_row.append(datum)

                    file_row = [x for x in file_row if x]

                    file_data.append(file_row)

                    file_data = [x for x in file_data if x != []]

                year_df = pd.DataFrame(file_data)
                year_df.insert(2, 'Season_Yr', year)

                team_df = team_df.append(year_df, ignore_index=True)

                browser.quit()

        team_df.drop(team_df.columns[[0, 3, 9]], axis=1, inplace=True)

        team_df.columns = ['Tm', 'Season_Yr', 'W', 'D', 'L', 'GF', 'GA', 'Pts', 'PPG', 'CS', 'FTS']

        self.team_df = team_df

    def clean_data(self, team_df):

        # Fill NaN when they exist: when the current season is still on the beginning
        team_df.fillna(0, inplace=True)

        team_df['CS'] = team_df['CS'].map(lambda x: x.rstrip('%'))
        team_df['FTS'] = team_df['FTS'].map(lambda x: x.rstrip('%'))

        # Convert the data to the proper data frame
        team_df = team_df.apply(pd.to_numeric, errors="ignore")

        team_df['CS'] /= 100.0
        team_df['FTS'] /= 100.0

        team_df.columns = team_df.columns.str.strip()
        team_df["Tm"] = team_df["Tm"].map(str.strip)

        team_df.to_csv("football_top5_team_stats_" + str(self.year1) + '_' + str(self.year2) + '.csv', mode='w+')

# x = AcquireFootballTop5TeamStats(2013, 2016)
# x()
