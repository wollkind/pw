__author__ = 'steve'
import random
from pw import *

if __name__ == '__main__':

    con = get_con()
    con.autocommit = True

    teams = list(range(1,97))
    levels = [Level.ml]#, Level.aaa, Level.lm]
    types = [StatType.hitting, StatType.pitching, StatType.fielding]
    leagues = [League.mays, League.williams]

    total_count = 0
    league_count = 0

    for league in leagues:
        league_count += 1

        year = get_league_date(league).year


        log("Starting {} {} ({} of {})".format(league.name, year))

        get_all_stats_for_league_year(league, year, teams, levels, types, con)


    con.close()