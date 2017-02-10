# coding: utf-8

import numpy as np


# get_ipython().magic(u'matplotlib inline')


class ModelNBA(object):
    from RunModelNBA import NBAMakePredictions
    from ScrapeMatchupDatetimeOddsTwoChoicesNBA import AcquireMatchupDatetimeOddsTwoChoices
    from SibylVsBookiesNBA import AcquireSibylVsBookiesNBA
    from ModelMetricsNBA import ModelMetricsNBA

    def __init__(self, current_season, feature_file, nba_db_name,
                 betbrain_upcoming_games_url, cs_team_stats_filename, league_name, upcoming_games_output_filename_us,
                 upcoming_games_output_filename_eu, oddsportal_url_fix, oddsportal_url_list_format):
        self.current_season = current_season
        self.feature_file = feature_file
        self.data = np.load(feature_file)
        self.tableau_input_filename = "nba_tableau_output_" + str(current_season) + ".csv"
        self.current_season = current_season
        self.X = self.data['X']
        self.y = self.data['y']
        self.nba_db_name = nba_db_name
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
        print "NBA Machine Learning process execution..."
        x = self.NBAMakePredictions(self.current_season, self.feature_file, self.nba_db_name)
        x()
        print "NBA Machine Learning process execution...OK\n"

        print "NBA Scraping odds and datetime from Betbrain.com process execution..."

        w = self.AcquireMatchupDatetimeOddsTwoChoices(
            self.season_over,
            self.betbrain_upcoming_games_url,
            self.cs_team_stats_filename, self.league_name,
            self.tableau_input_filename,
            self.upcoming_game_outputs_filename_us,
            self.upcoming_games_output_filename_eu)
        w()
        print "NBA Scraping odds and datetime from Betbrain.com process execution...OK\n"

        # ----------------------------------------------------------------------------

        self.season_over = w.season_over
        print self.league_name + ' season is over? : ' + self.season_over + '=> '
        if self.season_over == 'No':
            print "Moving on...\n"
        else:
            print "Season over => Stopping the NBA process\n"

        print "NBA Sibyl vs Bookies process execution..."
        v = self.AcquireSibylVsBookiesNBA(self.season_over, self.oddsportal_url_fix, self.oddsportal_url_list_format,
                                          self.cs_team_stats_filename, self.tableau_input_filename)
        v()
        print "NBA Sibyl vs Bookies process execution...OK\n"

        print "NBA ModelMetrics process execution..."

        u = self.ModelMetricsNBA(self.season_over, self.tableau_input_filename, self.upcoming_game_outputs_filename_us,
                                 self.cs_team_stats_filename)
        u()
        print "NBA ModelMetrics process execution...OK\n"


if __name__ == '__main__':
    x = ModelNBA(2017,
                 'nba_features_1980_2014.npz', 'nba_team_data_2017.db',
                 'https://www.betbrain.com/basketball/united-states/nba/',
                 'nba_team_stats_2017_2017.csv',
                 'NBA',
                 'NBA_Upcoming_Matchups_US_P_df.csv', 'NBA_Upcoming_Matchups_EU_P_df.csv',
                 'http://www.oddsportal.com/basketball/usa/nba/results/',
                 'http://www.oddsportal.com/basketball/usa/nba/results/#/page/{}/')
    x()

# Think to build the main section to run all of this from a terminal
