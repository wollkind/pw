__author__ = 'steve'

from pw import *

if __name__ == '__main__':

    con = mysql.connector.connect(host='localhost', user='njord', password='r905pyc', database='pw', unix_socket='/var/run/mysqld/mysqld.sock')

    con.autocommit = True

    # log("Cleaning stat tables")
    # cur = con.cursor()
    # cur.execute("SET @@session.sql_mode= ''")
    # cur.execute("truncate adv_hitting_stats")
    # cur.execute("truncate adv_pitching_stats")
    # cur.execute("truncate hitting_stats")
    # cur.execute("truncate pitching_stats")
    # cur.execute("truncate fielding_stats")

    for league in [League.williams]:
        current_year = get_league_date(league).year
        start_year = get_league_start_year(league)

        log("Get the fielding stats")
        years=range(start_year, current_year+1)

        for year in years:
            for division in range(1,5):
                season = get_season_from_year(league, year)
                log("Backfilling league {} fielding year {} division {}".format(league, year, division))
                get_pw_stats(league,division,Level.ml,season,StatType.fielding,StatGroup.basic, con)
                rest()

        log("Backfilling {}".format(league.name))
        for level in [Level.aaa, Level.ml, Level.lm]:
            log("Doing level {}".format(level))
            for type in [StatType.hitting, StatType.pitching]:
                log("Doing stattype {}".format(type))
                if level != Level.ml:
                    divisions = range(0,1)
                else:
                    divisions = range(1,5)

                for division in divisions:
                    log("Backfilling division {} level {} type {} basic".format(division, level.name, type.name))
                    get_pw_stats(league,division,level,-1,type,StatGroup.basic, con)

                    rest()

                    log("Backfilling division {} level {} type {} advanced".format(division, level.name, type.name))
                    get_pw_stats(league,division,level,-1,type,StatGroup.advanced, con)
                    rest()


    con.close()
