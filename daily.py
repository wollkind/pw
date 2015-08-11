__author__ = 'steve'

from pw import *


if __name__ == '__main__':


    #con = mysql.connector.connect(host='devbox-me', user='oleepoth', password='urcify', database='pw', port='3316')
    con = mysql.connector.connect(host='localhost', user='root', password='', database='pw')
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


            get_pw_players(league, year, 1, con)
            rest()
            get_pw_players(league, year, 2, con)
            rest()
            get_sign_now(league, 0, con)
            rest()
            get_sign_now(league, 1, con)
            rest()

            log("Note that we have processed this date")
            query = "insert into processed_dates (league_id, entry_date) values (%s, %s)"
            cur.execute(query, [league.value, cur_league_date])

        else:
            log("no stuff to do")

