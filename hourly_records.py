__author__ = 'steve'

from pw import *


if __name__ == '__main__':


    con = get_con()
    con.autocommit = True

    cur = con.cursor()
    cur.execute("SET @@session.sql_mode= ''")



    for league in list(League):
        log("Get {} date".format(league))
        cur_league_date = get_league_date(league)
        log("{} date {}".format(league.name, cur_league_date))
        get_standings(league, con)
