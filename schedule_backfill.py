__author__ = 'steve'
import random
from pw import *

if __name__ == '__main__':

    con = mysql.connector.connect(host='localhost', user='njord', password='r905pyc', database='pw', unix_socket='/var/run/mysqld/mysqld.sock')
    #con = mysql.connector.connect(host='localhost', user='root', password='', database='pw')

    con.autocommit = True



    teams = list(range(1,97))


    for league in [League.mays]:
        current_year = get_league_date(league).year
        start_year = get_league_start_year(league)


        years = list(range(current_year, start_year - 1, -1))
        random.shuffle(years)
        for year in years:
            season = get_season_from_year(league, year)
            log("Backfilling {} {}".format(league.name, year))


            random.shuffle(teams)
            for team_id in teams:
                get_team_schedule(league, team, season, con)
                rest()

con.close()
