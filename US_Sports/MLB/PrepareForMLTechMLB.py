# coding: utf-8

# In[13]:

import csv
import sqlite3 as lite

from pandas import *


class PrepareForML(object):
    # Prepares the raw data scraped from sports-reference.com and turns it into a
    # form that can be digested by the scikit-learn classes.

    def __init__(self, scoring_filename, cbb_db_name):
        self.scoring_filename = scoring_filename
        self.cbb_db_name = cbb_db_name

    def __call__(self, features_filename):
        # Looping through the csv file 'game_data_1981_to_2015.csv'
        # and creates a feature vector for each game played. 
        # The results are stored in an array 'features.npz' in the current directory

        con = lite.connect(self.cbb_db_name)
        with con:
            cur = con.cursor()

            features = []
            results = []
            with open(self.scoring_filename, 'rb') as csvfile:
                games = csv.reader(csvfile)
                games.next()

                for game in games:
                    feature, result = self.process_game(game, cur)

                    if result is not None:
                        features.append(feature)
                        results.append(result)

        # Save features and results to file
        features = np.vstack(features)
        results = np.array(results)
        np.savez(features_filename, X=features, y=results)

    @staticmethod
    def process_game(game, cursor):
        # The input frame is a list that contains the following elements:
        # Season_Yr, Visitor_Team, V_PTS, Home_Team, H_PTS
        # These elements refer to matchup. 
        # This function queries the SQL database 'cbb_db_name' and returns the difference and ratio 
        # between features(Home_Team) and features(Visitor_Team). The result of the match is the target variable
        # 1 if Home_Team scored more than Visitor_Team 0 otherwise

        query = 'SELECT * FROM Team_Stats WHERE Team = ? AND Season_Yr = ?'

        try:
            year, t1, p1, t2, p2 = game
            year, p1, p2 = map(int, [year, p1, p2])
            cursor.execute(query, (t1, year))
            feature1 = list(cursor.fetchone()[2::])
            cursor.execute(query, (t2, year))
            feature2 = list(cursor.fetchone()[2::])
            feature = np.array(feature2) - np.array(feature1)

            # Calculate result of game 
            if (p2 - p1) > 0:
                result = 1
            else:
                result = 0

            return feature, result

        except ValueError:
            return None, None

        except TypeError:
            return None, None

    def process_raw_data(self, team_data_csv_filename, what_to_do='sql'):
        # Processes csv file named 'team_data_csv_filename' containing team data. If what_to_do 
        # is set to 'csv' then a csv file is output. If set to 'sql'  then sqlite table named 'Team_Stats' is created 
        # in the database titled 'cbb_db_name'. 

        df = read_csv(team_data_csv_filename)
        features = ['R_per_G', 'PA', 'AB', 'B_R', 'B_H', '2B', '3B', 'B_HR', 'RBI', 'SB', 'CS', 'B_BB', 'B_SO', 'BA',
                    'OBP', 'SLG', 'OPS', 'OPS_Plus', 'TB', 'GDP', 'B_HBP', 'SH', 'SF', 'B_IBB', 'B_LOB', 'RA_per_G',
                    'WinLoss_Perc', 'ERA', 'CG', 'tSho', 'cSho', 'SV', 'IP', 'P_H', 'P_R', 'ER', 'P_HR', 'P_BB',
                    'P_IBB', 'P_SO', 'P_HBP', 'BK', 'WP', 'BF', 'ERA_Plus', 'FIP', 'WHIP', 'H9', 'HR9', 'BB9', 'SO9',
                    'SO_per_W', 'P_LOB']

        df_out = df[features]
        df_out.insert(0, 'Team', df['Tm'])
        df_out.insert(1, 'Season_Yr', df['Season_Yr'])

        if what_to_do == 'sql':
            # Export to SQL table
            con = lite.connect(self.cbb_db_name)
            with con:
                cur = con.cursor()
                df_out.to_sql('Team_Stats', con, if_exists='replace', index=False)
                # Add index to Team and Year columns
                cur.execute('CREATE INDEX tp_index ON Team_Stats(Team, Season_Yr);')
        elif what_to_do == 'csv':
            # Export to CSV file
            output_name = team_data_csv_filename.replace('.csv', '_processed.csv')
            df_out.to_csv(output_name, mode='w+')
