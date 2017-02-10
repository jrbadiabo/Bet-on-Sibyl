# coding: utf-8

import numpy as np
import sys


class ModelNHL(object):
    from RunModelNHL import NHLMakePredictions
    from ScrapeMatchupDatetimeOddsTwoChoicesNHL import AcquireMatchupDatetimeOddsTwoChoices
    from SibylVsBookiesNHL import AcquireSibylVsBookiesNHL
    from ModelMetricsNHL import ModelMetricsNHL

    def __init__(self, current_season, feature_file, nhl_db_name,
                 betbrain_upcoming_games_url, cs_team_stats_filename, league_name, upcoming_games_output_filename_us,
                 upcoming_games_output_filename_eu, oddsportal_url_fix, oddsportal_url_list_format):
        self.current_season = current_season
        self.feature_file = feature_file
        self.data = np.load(feature_file)
        self.tableau_input_filename = "nhl_tableau_output_" + str(current_season) + ".csv"
        self.current_season = current_season
        self.X = self.data['X']
        self.y = self.data['y']
        self.nhl_db_name = nhl_db_name
        self.betbrain_upcoming_games_url = betbrain_upcoming_games_url
        self.cs_team_stats_filename = cs_team_stats_filename
        self.league_name = league_name
        self.upcoming_game_outputs_filename_us = upcoming_games_output_filename_us
        self.upcoming_games_output_filename_eu = upcoming_games_output_filename_eu
        self.oddsportal_url_fix = oddsportal_url_fix
        self.oddsportal_url_list_format = oddsportal_url_list_format
        self.cs_team_stats_filename = cs_team_stats_filename
        self.season_over = 'No'

    def __call__(self):
        print "NHL Machine Learning process execution..."
        x = self.NHLMakePredictions(self.current_season, self.feature_file, self.nhl_db_name)
        x()
        print "NHL Machine Learning process execution...OK\n"

        print "NHL Scraping odds and datetime from Betbrain.com process execution..."
        w = self.AcquireMatchupDatetimeOddsTwoChoices(
            self.season_over,
            self.betbrain_upcoming_games_url,
            self.cs_team_stats_filename, self.league_name,
            self.tableau_input_filename,
            self.upcoming_game_outputs_filename_us,
            self.upcoming_games_output_filename_eu)
        w()
        print "NHL Scraping odds and datetime from Betbrain.com process execution...OK\n"

        # ----------------------------------------------------------------------------

        self.season_over = w.season_over
        print self.league_name + ' season is over? : ' + self.season_over + '=> '
        if self.season_over == 'No':
            print "Moving on...\n"
        else:
            print "Season over => Stopping the NHL process\n"

        # ----------------------------------------------------------------------------

        print "NHL Sibyl vs Bookies process execution..."
        v = self.AcquireSibylVsBookiesNHL(self.season_over, self.oddsportal_url_fix, self.oddsportal_url_list_format,
                                          self.cs_team_stats_filename, self.tableau_input_filename)
        v()
        print "NHL Sibyl vs Bookies process execution...OK\n"

        print "NHL ModelMetrics process execution..."
        u = self.ModelMetricsNHL(self.season_over, self.tableau_input_filename, self.upcoming_game_outputs_filename_us,
                                 self.cs_team_stats_filename)
        u()
        print "NHL ModelMetrics process execution...OK\n"


if __name__ == '__main__':
    x = ModelNHL(2017, 'nhl_features_2006_2015.npz', 'nhl_team_data_2017.db',
                 'https://www.betbrain.com/ice-hockey/united-states/nhl/', 'nhl_team_stats_2017_2017.csv', 'NHL',
                 'NHL_Upcoming_Matchups_US_P_df.csv', 'NHL_Upcoming_Matchups_EU_P_df.csv',
                 'http://www.oddsportal.com/hockey/usa/nhl/results/',
                 'http://www.oddsportal.com/hockey/usa/nhl/results/#/page/{}/')
    x()

# x = ModelNHL(2017, 'nhl_features_1980_2014.npz', 'nhl_team_data_2017.db',\
# 'https://www.betbrain.com/ice-hockey/united-states/nhl/', 'nhl_team_stats_2017_2017.csv', 'NHL',\
# 'NHL_Upcoming_Matchups_US_P_df.csv', 'NHL_Upcoming_Matchups_EU_P_df.csv',\
# 'http://www.oddsportal.com/hockey/usa/nhl/results/', 'http://www.oddsportal.com/hockey/usa/nhl/results/#/page/{}/')

# Think to build the main section to run all of this from a terminal
