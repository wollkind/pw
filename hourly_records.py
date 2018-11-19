__author__ = 'steve'

from pw import *
from datetime import date

if __name__ == '__main__':


    con = get_con()
    con.autocommit = True

    cur = con.cursor()
    cur.execute("SET @@session.sql_mode= ''")



    for league in list(League):
        log("Get {} date".format(league))
        cur_league_date = get_league_date(league)
        year = cur_league_date.year
        log("{} date {}".format(league.name, cur_league_date))
        if date(year, 4, 1)<= cur_league_date <= date(year, 9, 26):
            get_standings(league, con)
        else:
            log("Not in season")
