# coding: utf-8

import sys
import numpy as np


# get_ipython().magic(u'matplotlib inline')


class ModelNFL(object):
    from RunModelNFL import NFLMakePredictions
    from ScrapeMatchupDatetimeOddsTwoChoicesNFL import AcquireMatchupDatetimeOddsTwoChoices
    from SibylVsBookiesNFL import AcquireSibylVsBookiesNFL
    from ModelMetricsNFL import ModelMetricsNFL

    def __init__(self, current_season, feature_file, nfl_db_name,
                 betbrain_upcoming_games_url, cs_team_stats_filename, league_name, upcoming_game_outputs_filename_us,
                 upcoming_games_output_filename_eu, oddsportal_url_fix, oddsportal_url_list_format):
        self.current_season = current_season
        self.feature_file = feature_file
        self.data = np.load(feature_file)
        self.tableau_input_filename = "nfl_tableau_output_" + str(current_season) + ".csv"
        self.current_season = current_season
        self.X = self.data['X']
        self.y = self.data['y']
        self.nfl_db_name = nfl_db_name
        self.betbrain_upcoming_games_url = betbrain_upcoming_games_url
        self.cs_team_stats_filename = cs_team_stats_filename
        self.league_name = league_name
        self.upcoming_game_outputs_filename_us = upcoming_game_outputs_filename_us
        self.upcoming_games_output_filename_eu = upcoming_games_output_filename_eu
        self.oddsportal_url_fix = oddsportal_url_fix
        self.oddsportal_url_list_format = oddsportal_url_list_format
        self.cs_team_stats_filename = cs_team_stats_filename
        self.season_over = 'No'

    def __call__(self):
        print "NFL Machine Learning process execution..."
        x = self.NFLMakePredictions(self.current_season, self.feature_file, self.nfl_db_name)
        x()
        print "NFL Machine Learning process execution...OK\n"

        print "NFL Scraping odds and datetime from Betbrain.com process execution..."
        w = self.AcquireMatchupDatetimeOddsTwoChoices(
            self.season_over,
            self.betbrain_upcoming_games_url,
            self.cs_team_stats_filename, self.league_name,
            self.tableau_input_filename,
            self.upcoming_game_outputs_filename_us,
            self.upcoming_games_output_filename_eu)
        w()

        # ----------------------------------------------------------------------------

        self.season_over = w.season_over
        print self.league_name + ' season is over? : ' + self.season_over + '=> '
        if self.season_over == 'No':
            print "Moving on...\n"
        else:
            print "Season over => Stopping the NFL process\n"

        # ----------------------------------------------------------------------------
        print "NFL Sibyl vs Bookies process execution..."
        v = self.AcquireSibylVsBookiesNFL(self.season_over, self.oddsportal_url_fix, self.oddsportal_url_list_format,
                                          self.cs_team_stats_filename, self.tableau_input_filename)
        v()
        print "NFL Sibyl vs Bookies process execution...OK\n"

        print "NFL ModelMetrics process execution..."
        u = self.ModelMetricsNFL(self.season_over, self.tableau_input_filename, self.upcoming_game_outputs_filename_us,
                                 self.cs_team_stats_filename)
        u()
        print "NFL ModelMetrics process execution...OK\n"


if __name__ == '__main__':
    x = ModelNFL(2016, 'nfl_features_2000_2015.npz', 'nfl_team_data_2016.db',
                 'https://www.betbrain.com/am-football/united-states/nfl/', 'nfl_team_stats_2016_2016.csv', 'NFL',
                 'NFL_Upcoming_Matchups_US_P_df.csv', 'NFL_Upcoming_Matchups_EU_P_df.csv',
                 'http://www.oddsportal.com/american-football/usa/nfl/results/',
                 'http://www.oddsportal.com/american-football/usa/nfl/results/#/page/{}/')
    x()

# x = Model_NFL(2016, 'nfl_features_2000_2015.npz', 'nfl_team_data_2016.db',\
# 'https://www.betbrain.com/am-football/united-states/nfl/', 'nfl_team_stats_2016_2016.csv', 'NFL',\
# 'NFL_Upcoming_Matchups_US_P_df.csv', 'NFL_Upcoming_Matchups_EU_P_df.csv',\
# 'http://www.oddsportal.com/american-football/usa/nfl/results/',\
#  'http://www.oddsportal.com/american-football/usa/nfl/results/#/page/{}/')

# Think to build the main section to run all of this from a terminal
