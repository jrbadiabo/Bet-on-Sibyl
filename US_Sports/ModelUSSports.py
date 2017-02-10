from MLB.ModelMLB import ModelMLB

from NBA.ModelNBA import ModelNBA
from NFL.ModelNFL import ModelNFL
from NHL.ModelNHL import ModelNHL
from ModelMetricsUSSports import ModelMetricsUSSports

print "-------------------US SPORTS MODEL EXECUTION------------------------"

print "Initialisation ModelMLB...\n\n"
w = ModelMLB(2016,
             'C:\Users\jbadiabo\PycharmProjects\Sibyl\US_Sports\MLB\mlb_1980_2014_features.npz',
             'mlb_team_data_2016.db',
             'https://www.betbrain.com/baseball/united-states/mlb/',
             'mlb_team_stats_2016_2016.csv',
             'MLB',
             'MLB_Upcoming_Matchups_US_P_df.csv',
             'MLB_Upcoming_Matchups_EU_P_df.csv',
             'http://www.oddsportal.com/baseball/usa/mlb/results/',
             'http://www.oddsportal.com/baseball/usa/mlb/results/#/page/{}/')

print "ModelMLB execution...\n"
w()
print "ModelMLB execution... OK\n"

print "Initialisation ModelNBA...\n"
x = ModelNBA(2017,
             'C:\Users\jbadiabo\PycharmProjects\Sibyl\US_Sports\NBA\\nba_features_1980_2014.npz',
             'nba_team_data_2017.db',
             'https://www.betbrain.com/basketball/united-states/nba/',
             'nba_team_stats_2017_2017.csv',
             'NBA',
             'NBA_Upcoming_Matchups_US_P_df.csv',
             'NBA_Upcoming_Matchups_EU_P_df.csv',
             'http://www.oddsportal.com/basketball/usa/nba/results/',
             'http://www.oddsportal.com/basketball/usa/nba/results/#/page/{}/')

print "ModelNBA execution...\n"
x()
print "ModelNBA execution...OK\n"

print "Initialisation ModelNFL...\n"
y = ModelNFL(2016,
             'C:\Users\jbadiabo\PycharmProjects\Sibyl\US_Sports\NFL\\nfl_features_2000_2015.npz',
             'nfl_team_data_2016.db',
             'https://www.betbrain.com/am-football/united-states/nfl/',
             'nfl_team_stats_2016_2016.csv',
             'NFL',
             'NFL_Upcoming_Matchups_US_P_df.csv',
             'NFL_Upcoming_Matchups_EU_P_df.csv',
             'http://www.oddsportal.com/american-football/usa/nfl/results/',
             'http://www.oddsportal.com/american-football/usa/nfl/results/#/page/{}/')

print "ModelNFL execution...\n"
y()
print "ModelNFL execution...OK\n"

print "Initialisation ModelNHL...\n"
z = ModelNHL(2017,
             'C:\Users\jbadiabo\PycharmProjects\Sibyl\US_Sports\NHL\\nhl_features_2006_2015.npz',
             'nhl_team_data_2017.db',
             'https://www.betbrain.com/ice-hockey/united-states/nhl/',
             'nhl_team_stats_2017_2017.csv',
             'NHL',
             'NHL_Upcoming_Matchups_US_P_df.csv',
             'NHL_Upcoming_Matchups_EU_P_df.csv',
             'http://www.oddsportal.com/hockey/usa/nhl/results/',
             'http://www.oddsportal.com/hockey/usa/nhl/results/#/page/{}/')

print "ModelNHL execution...\n"
z()
print "ModelNHL execution...OK\n"

print "Initialisation ModelMetricsUSSports...\n"
v = ModelMetricsUSSports(
    "us_sports_tableau_output.csv",
    "us_sports_upcoming_matchups_us_p_df.csv",
    "us_sports_team_names_list.csv")

print "ModelMetricsUSSports execution...\n"
v()
print "ModelMetricsUSSports execution...OK\n"

print "-------------------US SPORTS MODEL EXECUTION------------------------"
print "-----------------------------DONE!-----------------------------------"
