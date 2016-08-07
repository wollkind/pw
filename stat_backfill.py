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
    levels = [Level.ml, Level.aaa, Level.lm]
    types = [StatType.hitting, StatType.pitching]
    leagues = [League.mays]

    total_count = 0
    league_count = 0

    for league in leagues:
        league_count+=1

        current_year = get_league_date(league).year
        start_year = get_league_start_year(league)

        log("Starting league {} ({} of {})".format(league, league_count, len(leagues)))
        years = list(range(current_year, start_year - 1, -1))

        year_count = 0
        for year in years:
            year_count+=1
            season = get_season_from_year(league, year)
            log("Starting {} {} ({} of {})".format(league.name, year, year_count, len(years)))


            random.shuffle(teams)
            team_count = 0
            for team_id in teams:
                team_count+=1
                log("Starting {} {} {} ({} of {})".format(league.name, year, team_id, team_count, len(teams)))
                random.shuffle(levels)

                level_count = 0

                for level in levels:
                    log("Starting {} {} {} {} ({} of {})".format(league.name, year, team_id, level, level_count, len(levels)))
                    random.shuffle(types)
                    for type in types:
                        total_count+=1
                        log("Working on {} of {}".format(total_count, len(leagues)*len(years)*len(teams)*len(levels)*len(types)))
                        get_pw_stats(league, team_id, level, season, type, StatGroup.basic, con)
                        rest()
                        get_pw_stats(league, team_id, level, season, type, StatGroup.advanced, con)

                        rest()
                get_pw_stats(league, team_id, Level.ml, season, StatType.fielding, StatGroup.basic, con)
                rest()

con.close()
