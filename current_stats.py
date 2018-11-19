__author__ = 'steve'
import random
from pw import *
from datetime import date

if __name__ == '__main__':

    con = get_con()
    con.autocommit = True

    teams = list(range(1,97))
    levels = [Level.ml]#, Level.aaa, Level.lm]
    types = [StatType.hitting, StatType.pitching, StatType.fielding]
    leagues = [League.mays, League.williams]


    for league in leagues:

        league_date = get_league_date(league).year
        year = league_date.year
        season_start = date(year, 4, 1)

        if league_date < season_start:
            log("season hasn't started yet for {}".format(league.name))
            continue

        log("Starting {} {}".format(league.name, year))

        get_all_stats_for_league_year(league, year, teams, levels, types, con, True)


    con.close()