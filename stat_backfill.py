__author__ = 'steve'
import random
from pw import *

if __name__ == '__main__':

    con = mysql.connector.connect(host='localhost', user='njord', password='r905pyc', database='pw', unix_socket='/var/run/mysqld/mysqld.sock')
    #con = mysql.connector.connect(host='localhost', user='root', password='', database='pw')

    con.autocommit = True

    log("Cleaning stat tables")
    cur = con.cursor()
    cur.execute("SET @@session.sql_mode= ''")
    cur.execute("truncate adv_hitting_stats")
    cur.execute("truncate adv_pitching_stats")
    cur.execute("truncate hitting_stats")
    cur.execute("truncate pitching_stats")
    cur.execute("truncate fielding_stats")

    teams = list(range(1,97))
    levels = [Level.ml, Level.aaa, Level.lm]
    types = [StatType.hitting, StatType.pitching]

    for league in [League.mays]:
        current_year = get_league_date(league).year
        start_year = get_league_start_year(league)

        log("Get the fielding stats")
        years = list(range(current_year, start_year - 1, -1))
        random.shuffle(years)
        for year in years:
            season = get_season_from_year(league, year)
            log("Backfilling {} {}".format(league.name, year))


            random.shuffle(teams)
            for team_id in teams:
                log("Doing team {}".format(team_id))
                random.shuffle(levels)
                for level in levels:
                    log("Doing level {}".format(level))
                    random.shuffle(types)
                    for type in types:
                        log("Doing stattype {}".format(type))

                        log("Backfilling team {} level {} type {} basic".format(team_id, level.name, type.name))
                        get_pw_stats(league, team_id, level, season, type, StatGroup.basic, con)
                        rest()
                        get_pw_stats(league, team_id, level, season, type, StatGroup.advanced, con)

                        rest()
                get_pw_stats(league, team_id, Level.ml, season, StatType.fielding, StatGroup.basic, con)
                rest()

con.close()
