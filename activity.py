__author__ = 'steve'

from pw import *


if __name__ == '__main__':


    con = mysql.connector.connect(host='localhost', user='njord', password='r905pyc', database='pw', unix_socket='/var/run/mysqld/mysqld.sock')
    con.autocommit = True

    cur = con.cursor()
    cur.execute("SET @@session.sql_mode= ''")



    for league in list(League):
        get_team_activity(league, con)
