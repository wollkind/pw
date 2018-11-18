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


    for league in leagues:

        year = get_league_date(league).year

        log("Starting {} {} ({} of {})".format(league.name, year))

        get_all_stats_for_league_year(league, year, teams, levels, types, con)


    con.close()