__author__ = 'steve'

from pw import *


if __name__ == '__main__':


    con = mysql.connector.connect(host='localhost', user='njord', password='r905pyc', database='pw', unix_socket='/var/run/mysqld/mysqld.sock')
    con.autocommit = True

    cur = con.cursor()
    cur.execute("SET @@session.sql_mode= ''")



    for league in list(League):

        log("Get {} date".format(league))
        cur_league_date = get_league_date(league)
        log("{} date {}".format(league.name, cur_league_date))

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
