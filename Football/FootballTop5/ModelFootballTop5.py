# coding: utf-8

# In[1]:

import sys
import numpy as np


# get_ipython().magic(u'matplotlib inline')

class ModelFootballTop5(object):
    from RunModelFootballTop5 import FootballTop5MakePredictions
    from ScrapeMatchupDatetimeOddsThreeChoicesFootballTop5 import AcquireMatchupDatetimeOddsThreeChoices
    from SibylVsBookiesFootballTop5 import AcquireSibylVsBookiesFootballTop5
    from ModelMetricsFootballTop5 import ModelMetricsFootballTop5

    def __init__(self, current_season, feature_file, football_top5_db_name, betbrain_upcoming_games_url,
                 cs_team_stats_filename, category_name, oddsportal_url_fix, oddsportal_url_list_format):

        self.current_season = current_season
        self.feature_file = feature_file
        self.data = np.load(feature_file)
        self.tableau_input_filename = "football_top5_tableau_output_" + str(current_season) + ".csv"
        self.current_season = current_season
        self.X = self.data['X']
        self.y = self.data['y']
        self.football_top5_db_name = football_top5_db_name
        self.betbrain_upcoming_games_url = betbrain_upcoming_games_url
        self.cs_team_stats_filename = cs_team_stats_filename
        self.category_name = category_name
        self.oddsportal_url_fix = oddsportal_url_fix
        self.oddsportal_url_list_format = oddsportal_url_list_format
        self.cs_team_stats_filename = cs_team_stats_filename
        self.leagues = ['Bundesliga', 'Primera_Division', 'Serie_A', 'Premier_League', 'Ligue_1']

    def __call__(self):

        x = self.FootballTop5MakePredictions(self.current_season, self.feature_file, self.football_top5_db_name)
        x()

        w = self.AcquireMatchupDatetimeOddsThreeChoices(self.betbrain_upcoming_games_url,
                                                        self.cs_team_stats_filename, self.category_name,
                                                        self.tableau_input_filename)
        w()

        # passing if we encounter an  "AttributeError" -> meaning that there is no upcoming games 
        # -> so we don't update the upcoming game table 
        try:

            v = self.AcquireSibylVsBookiesFootballTop5(self.oddsportal_url_fix, self.oddsportal_url_list_format,
                                                       self.cs_team_stats_filename, self.tableau_input_filename)
            v()

            u = self.ModelMetricsFootballTop5(self.tableau_input_filename, self.category_name, self.leagues,
                                              self.cs_team_stats_filename)

            u()
        except AttributeError:  # meaning the dataframe for upcoming could not been scraped ->
            #  so we don't update the upcoming game table
            pass

            # x = ModelFootballTop5(2017, 'football_top5_features_2013_2016.npz', 'football_top5_team_data_2017.db',\
            # 'https://www.betbrain.com/football/{country}/{league}/',
            #  'football_top5_team_stats_2017_2017.csv', 'FootballTop5',\
            #  'http://www.oddsportal.com/soccer/{country}/{league}/results/',
            #  'http://www.oddsportal.com/soccer/{country}/{league}/results/#/page/{}/')

            # Think to build the main section to run all of this from a terminal


# ex of use
if __name__ == '__main__':
    x = ModelFootballTop5(2017, 'football_top5_features_2013_2016.npz', 'football_top5_team_data_2017.db', \
                          'https://www.betbrain.com/football/{country}/{league}/',
                          'football_top5_team_stats_2017_2017.csv',
                          'FootballTop5', 'http://www.oddsportal.com/soccer/{country}/{league}/results/',
                          'http://www.oddsportal.com/soccer/{country}/{league}/results/#/page/{}/')
    x()
