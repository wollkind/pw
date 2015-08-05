__author__ = 'steve'

from pw import *


if __name__ == '__main__':

    global con
    con = mysql.connector.connect(host='devbox-me', user='oleepoth', password='urcify', database='pw', port='3316')
    con.autocommit = True

    cur = con.cursor()
    cur.execute("SET @@session.sql_mode= ''")

    for league in list(League):
        log("Get league date")
        cur_league_date = get_league_date(league)
        log("{} date {}".format(league.name, cur_league_date))

        log("Get last processed league date")
        cur.execute("select max(entry_date) d from processed_dates where league_id=%s",[league.value])
        row = cur.fetchone()
        log("Last saw {}".format(row[0]))

        if row[0] != cur_league_date:
            log("do stuff")

            year = cur_league_date.year
            season = get_season_from_year(league, year)

            cur.execute("drop table if exists hitters_prev")
            cur.execute("drop table if exists pitchers_prev")
            cur.execute("create table hitters_prev select * from hitters where league_id=%s and year=%s",[league.value, year])
            cur.execute("create table pitchers_prev select * from pitchers where league_id=%s and year=%s",[league.value, year])

            get_pw_players(league, year, 1, con)
            rest()
            get_pw_players(league, year, 2, con)
            rest()
            get_sign_now(league, 0, con)
            rest()
            get_sign_now(league, 1, con)
            rest()

            # for level in [Level.aaa, Level.ml, Level.lm]:
            #     log("Doing level {}".format(level))
            #     for type in list(StatType):
            #         log("Doing stattype {}".format(type))
            #         if level != Level.ml:
            #             if type == StatType.fielding:
            #                 log("Skipping")
            #                 continue
            #             divisions = range(0,1)
            #         else:
            #             divisions = range(1,5)
            #
            #         for division in divisions:
            #             log("Getting division {} level {} type {} basic".format(division, level.name, type.name))
            #             get_pw_stats(league,division,level,season,type,StatGroup.basic, con)
            #
            #             rest()
            #             if type != StatType.fielding:
            #                 log("Getting division {} level {} type {} advanced".format(division, level.name, type.name))
            #                 get_pw_stats(league,division,level,season,type,StatGroup.advanced, con)
            #                 rest()


            log("Note that we have processed this date")
            query = "insert into processed_dates (league_id, entry_date) values (%s, %s)"
            cur.execute(query, [league.value, cur_league_date])

        else:
            log("no stuff to do")

