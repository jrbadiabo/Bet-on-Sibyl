from pandas import *
import itertools

# -------------------------------------------------------
mlb_tableau_df = read_csv("C:\Users\jbadiabo\PycharmProjects\Sibyl\US_Sports\MLB\mlb_tableau_input_2016.csv")
nba_tableau_df = read_csv("C:\Users\jbadiabo\PycharmProjects\Sibyl\US_Sports\NBA\\nba_tableau_output_2017.csv")
nfl_tableau_df = read_csv("C:\Users\jbadiabo\PycharmProjects\Sibyl\US_Sports\NFL\\nfl_tableau_output_2016.csv")
nhl_tableau_df = read_csv("C:\Users\jbadiabo\PycharmProjects\Sibyl\US_Sports\NHL\\nhl_tableau_output_2017.csv")
# ------------------------------------------------------

upco_nba = read_csv("C:\Users\jbadiabo\PycharmProjects\Sibyl\US_Sports\NBA\\NBA_Upcoming_Matchups_US_P_df.csv")
upco_nfl = read_csv("C:\Users\jbadiabo\PycharmProjects\Sibyl\US_Sports\NFL\\NFL_Upcoming_Matchups_US_P_df.csv")
upco_nhl = read_csv("C:\Users\jbadiabo\PycharmProjects\Sibyl\US_Sports\NHL\\NHL_Upcoming_Matchups_US_P_df.csv")
upco_mlb = read_csv("C:\Users\jbadiabo\PycharmProjects\Sibyl\US_Sports\MLB\MLB_Upcoming_Matchups_US_P_df.csv")
upco_mlb['League'] = 'MLB'
upco_mlb['True_Result'] = upco_mlb['True_Result_U']
upco_mlb.drop('True_Result_U', axis=1, inplace=True)

# ------------------------------------------------------

mlb_team_stat_df = read_csv('C:\Users\jbadiabo\PycharmProjects\Sibyl\US_Sports\MLB\mlb_team_stats_2016.csv')
nba_team_stat_df = read_csv('C:\Users\jbadiabo\PycharmProjects\Sibyl\US_Sports\NBA\\nba_team_stats_2017_2017.csv')
nba_team_stat_df['Tm'] = nba_team_stat_df['Team']
nfl_team_stat_df = read_csv('C:\Users\jbadiabo\PycharmProjects\Sibyl\US_Sports\NFL\\nfl_team_stats_2016_2016.csv')
nhl_team_stat_df = read_csv('C:\Users\jbadiabo\PycharmProjects\Sibyl\US_Sports\NHL\\nhl_team_stats_2017_2017.csv')

mlb_team_stat_df = read_csv('C:\Users\jbadiabo\PycharmProjects\Sibyl\US_Sports\MLB\mlb_team_stats_2016.csv')
nba_team_stat_df = read_csv('C:\Users\jbadiabo\PycharmProjects\Sibyl\US_Sports\NBA\\nba_team_stats_2017_2017.csv')
nba_team_stat_df['Tm'] = nba_team_stat_df['Team']
nfl_team_stat_df = read_csv('C:\Users\jbadiabo\PycharmProjects\Sibyl\US_Sports\NFL\\nfl_team_stats_2016_2016.csv')
nhl_team_stat_df = read_csv('C:\Users\jbadiabo\PycharmProjects\Sibyl\US_Sports\NHL\\nhl_team_stats_2017_2017.csv')


def get_team_name_list(mlb_df, nba_df, nfl_df, nhl_df):
    concat_name_list = []

    for i in [mlb_df, nba_df, nfl_df, nhl_df]:
        concat_name_list.append(i['Tm'])

    return concat_name_list


team_name_list = get_team_name_list(mlb_team_stat_df, nba_team_stat_df, nfl_team_stat_df, nhl_team_stat_df)
us_sports_team_names_list = list(itertools.chain.from_iterable(team_name_list))
us_sports_team_names_df = DataFrame(us_sports_team_names_list, columns=['Tm'])


def get_tableau_df(mlb_tableau, nba_tableau, nfl_tableau, nhl_tableau):
    frames = [mlb_tableau, nba_tableau, nfl_tableau, nhl_tableau]

    us_sports_df = concat(frames)

    return us_sports_df


us_sports_tableau_df = get_tableau_df(mlb_tableau_df, nba_tableau_df, nfl_tableau_df, nhl_tableau_df)


def get_upco_df(up_mlb, up_nba, up_nfl, up_nhl):
    frames = [up_mlb, up_nba, up_nfl, up_nhl]

    us_sports_upco_df = concat(frames)

    return us_sports_upco_df


us_sports_upco_df = get_upco_df(upco_mlb, upco_nba, upco_nfl, upco_nhl)

us_sports_tableau_df.to_csv('us_sports_tableau_output.csv', mode='w+', index=False)
us_sports_upco_df.to_csv('us_sports_upcoming_matchups_us_p_df.csv', mode='w+', index=False)
us_sports_team_names_df.to_csv('us_sports_team_names_list.csv', mode='w+', index=False)
