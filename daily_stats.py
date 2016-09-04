__author__ = 'steve'

from pw import *


if __name__ == '__main__':

    con = get_con()
    con.autocommit = True

    cur = con.cursor()
    cur.execute("SET @@session.sql_mode= ''")

    teams = list(range(1,97))
    levels = [Level.ml, Level.aaa, Level.lm]
    types = [StatType.hitting, StatType.pitching]
    leagues = [League.mays, League.ruth]

    for league in list(League):
        log("Get {} date".format(league))
        cur_league_date = get_league_date(league)
        log("{} date {}".format(league.name, cur_league_date))

        year = cur_league_date.year
        season = get_season_from_year(league, year)

        cur.execute("select max(entry_date) d from processed_dates where league_id=%s", [league.value])
        row = cur.fetchone()
        log("Last saw {}".format(row[0]))

        if row[0] != cur_league_date:
            log("do stuff")

            get_all_stats_for_league_year(league, year, teams, levels, types, con, True)

            log("Note that we have processed this date")
            query = "insert into processed_dates (league_id, entry_date) values (%s, %s)"
            cur.execute(query, [league.value, cur_league_date])

        else:
            log("no stuff to do")

