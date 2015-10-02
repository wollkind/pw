__author__ = 'steve'

from pw import *


if __name__ == '__main__':


    #con = mysql.connector.connect(host='devbox-me', user='oleepoth', password='urcify', database='pw', port='3316')
    con = mysql.connector.connect(host='localhost', user='root', password='', database='pw')
    con.autocommit = True

    cur = con.cursor()
    cur.execute("SET @@session.sql_mode= ''")

    for league in [League.ruth]:
        log("Get {} date".format(league))
        cur_league_date = get_league_date(league)
        log("{} date {}".format(league.name, cur_league_date))

        cur.execute("select max(entry_date) d from processed_dates where league_id=%s",[league.value])
        row = cur.fetchone()
        log("Last saw {}".format(row[0]))

        if row[0] != cur_league_date:
            log("do stuff")

            year = cur_league_date.year
            season = get_season_from_year(league, year)

            get_pw_players(league, year, 1, con)
            rest()
            get_pw_players(league, year, 2, con)
            rest()
            get_sign_now(league, 0, con)
            rest()
            get_sign_now(league, 1, con)
            rest()
            get_team_activity(league, con)

            # for division in range(1,5):
            #     season = get_season_from_year(league, year)
            #     log("Getting fielding for division {}".format(division))
            #     get_pw_stats(league, division, Level.ml, season, StatType.fielding, StatGroup.basic, con)
            #     rest()
            #
            #
            # for level in [Level.aaa, Level.ml, Level.lm]:
            #     log("Doing level {}".format(level))
            #     for type in [StatType.hitting, StatType.pitching]:
            #         log("Doing stattype {}".format(type))
            #         if level != Level.ml:
            #             divisions = range(0,1)
            #         else:
            #             divisions = range(1,5)
            #
            #         for division in divisions:
            #             log("Backfilling division {} level {} type {} basic".format(division, level.name, type.name))
            #             get_pw_stats(league, division, level, season, type, StatGroup.basic, con)
            #
            #             rest()
            #
            #             log("Backfilling division {} level {} type {} advanced".format(division, level.name, type.name))
            #             get_pw_stats(league, division, level, season, type, StatGroup.advanced, con)
            #             rest()



            log("Note that we have processed this date")
            query = "insert into processed_dates (league_id, entry_date) values (%s, %s)"
            cur.execute(query, [league.value, cur_league_date])

        else:
            log("no stuff to do")

