__author__ = 'steve'
import random
from pw import *

if __name__ == '__main__':

    con = get_con()
    con.autocommit = True

    # log("Cleaning stat tables")
    # cur = con.cursor()
    # cur.execute("SET @@session.sql_mode= ''")
    # cur.execute("truncate adv_hitting_stats")
    # cur.execute("truncate adv_pitching_stats")
    # cur.execute("truncate hitting_stats")
    # cur.execute("truncate pitching_stats")
    # cur.execute("truncate fielding_stats")

    teams = list(range(1,97))
    levels = [Level.ml]#, Level.aaa, Level.lm]
    types = [StatType.hitting, StatType.pitching, StatType.fielding]
    leagues = [League.mays, League.williams]

    total_count = 0
    league_count = 0

    for league in leagues:
        league_count += 1

        current_year = get_league_date(league).year - 1

        start_year = get_league_start_year(league)

        log("Starting league {} ({} of {})".format(league, league_count, len(leagues)))
        years = list(range(current_year, start_year - 1, -1))

        year_count = 0
        random.shuffle(years)
        for year in years:
            year_count+=1
            log("Starting {} {} ({} of {})".format(league.name, year, year_count, len(years)))

            get_all_stats_for_league_year(league, year, teams, levels, types, con)


    con.close()
