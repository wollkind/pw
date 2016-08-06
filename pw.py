__author__ = 'steve'

from bs4 import BeautifulSoup
import urllib
import mysql.connector
import csv
import re
from io import StringIO
import time
import datetime
from enum import IntEnum
from random import randint
from time import sleep


class League(IntEnum):
    mays = 6
    ruth = 4



class Level(IntEnum):
    all = 0
    ml = 5
    playoffs = 6
    aaa = 4
    lm = 3


class StatType(IntEnum):
    hitting = 0
    pitching = 1
    fielding = 2


class StatGroup(IntEnum):
    basic = 0
    advanced = 1


def get_league_start_year(league):
    if league==League.ruth:
        return 2013
    else:
        return 2014


def log(message):
    print("[{}] {}".format(datetime.datetime.now(), message))


def rest():
    sleeptime = randint(3, 6)
    log("Sleeping {}".format(sleeptime))
    sleep(sleeptime)


def get_year_from_season(league_id, season):
    if league_id < 6:
        return 2012 + season
    else:
        return 2013 + season


def get_season_from_year(league_id, year):
    if league_id < 6:
        return year - 2012
    else:
        return year - 2013


def to_insert(table, con):
    cur = con.cursor()

    cur.execute("SHOW columns FROM {}".format(table))
    columns = [column[0] for column in cur.fetchall() if column[0] != 'id']
    log(len(columns))
    insert_string = ", ".join(['%s'] * len(columns))

    query_string = 'INSERT INTO {} ({}) VALUES ({});'.format(table, ','.join(columns), insert_string).replace('\'\'',
                                                                                                              'NULL')

    return query_string


def convert(val):
    lookup = {'k': 1000, 'm': 1000000, 'b': 1000000000}
    unit = val[-1]

    number = float(val[1:-1])

    if unit in lookup:
        return lookup[unit] * number
    return int(val)


def get_sign_now(league, pos, con):
    cur = con.cursor()
    cur.execute("DELETE from sign_nows WHERE pos=%s and league_id=%s", [pos,league.value])

    url = "http://www.pennantwars.com/freeAgents.php?l={}&pos={}".format(league, pos)
    log("reading " + url)
    html = urllib.request.urlopen(url).read().decode('utf-8', errors='ignore')
    log("gathering data")
    soup = BeautifulSoup(html, "lxml")
    table = soup.find("table", "fulltable")

    p = re.compile(".*p=(\d+).*")

    headers = [header.text for header in table.find_all('th')]

    rows = []

    for row in table.find_all('tr'):

        m = p.match(str(row))

        if m:
            player_id = m.group(1)

            vals = row.find_all('td')
            spans = vals[-1].find_all('span')
            salary = spans[-1]
            dollars = salary.string
            if dollars == 'Sign Now':
                dollars = '$200m'

            newrow = [player_id, str(convert(dollars)), str(league.value),pos]

            rows.append(newrow)

    # log("writing csv")
    # with open('sign_now_file.csv', 'w') as f:
    #     writer = csv.writer(f)
    #     writer.writerow(headers)
    #     writer.writerows(row for row in rows if row)

    log("writing to database")
    cur = con.cursor()
    query_string = to_insert('sign_nows', con)
    cur.executemany(query_string, rows)


def get_pw_players(league, year, h, con):
    if h == 1:
        table = 'hitters'
    else:
        table = 'pitchers'

    cur = con.cursor()

    cur.execute("DELETE from {}_prev WHERE league_id=%s and year=%s".format(table), [league.value, year])
    cur.execute("INSERT into {}_prev SELECT * from {} where league_id=%s and year=%s".format(table, table), [league.value, year])

    cur.execute("DELETE from {} WHERE league_id=%s and year=%s".format(table), [league.value, year])


    url = "http://www.pennantwars.com/exportPlayers.php?l={}&h={}".format(league, h)

    log("reading " + url)
    html = urllib.request.urlopen(url).read().decode('utf-8', errors='ignore')

    log("replacing DL")
    html = html.replace("<span style='font-weight:bold;color:rgb(180, 47, 47)'>DL</div>", "DL")

    # log("writing csv")
    # with open("players-{}-{}-{}".format(league, year, h), "w") as text_file:
    #     text_file.write(html)

    f = StringIO(html)

    log("converting to csv")
    reader = csv.reader(f)
    your_list = list(reader)
    log("massaging data")

    newrows = [[league.value, str(year)] + [None if not x else x for x in row] for row in your_list[1:]]

    query_string = to_insert(table, con)

    log("saving to database")
    cur.executemany(query_string, newrows)


def get_team_schedule(league, team, season, con):
    ## delete this set of rows from games table
    year = get_year_from_season(league, season)

    cur = con.cursor()
    cur.execute("DELETE from schedule_and_results WHERE league_id=%s and team_id=%s and year=%s",
                [league.value, team, year])


    url = "http://www.pennantwars.com/team.php?l={}&t={}&tab=2&xseason={}".format(league.value, team,season)
    log(url)
    html = urllib.request.urlopen(url).read().decode('utf-8', errors='ignore')

    log("making soup")
    soup = BeautifulSoup(html, "lxml")
    tables = soup.find_all("table", id=False, class_="fulltable")
    log("done")

    result_rows=[]

    for table in tables:
        rows = table.find_all("tr", id=False)
        for row in rows:
            cells = row.find_all("td")
            if len(cells)<2:
                continue

            date = cells[0].text.split("/")
            strdate=str(year)+"-"+date[0]+"-"+date[1]
            log(strdate)

            result = cells[2].text
            resultex = re.compile("([WL]), (\d+) - (\d+)")



            tex = re.compile(".*t=(\d+).*")
            gex = re.compile(".*g=(\d+).*")
            m=tex.match(str(row))

            if m:
                opponent = m.group(1)
                game = None
                g = gex.match(str(row))
                if g:
                    game = g.group(1)

                resm = resultex.match(result)
                result_char=None
                rs=None
                ra=None
                if resm:
                    result_char=resm.group(1)
                    rs=resm.group(2)
                    ra=resm.group(3)

                newrow = [league.value, team, year, str(strdate), str(game), str(opponent), str(result_char), rs, ra]
                result_rows.append(newrow)




    log("writing to database")
    insert_sql = to_insert("schedule_and_results", con)

    cur = con.cursor()
    cur.executemany(insert_sql, result_rows)




def get_pw_stats(league, team, level, season, tab, xtype, con):
    if tab == StatType.fielding:
        sqltable = 'fielding_stats'
    elif tab == StatType.hitting:
        if xtype == StatGroup.basic:
            sqltable = 'hitting_stats'
        else:
            sqltable = 'adv_hitting_stats'
    elif tab == StatType.pitching:
        if xtype == StatGroup.basic:
            sqltable = 'pitching_stats'
        else:
            sqltable = 'adv_pitching_stats'

    cur = con.cursor()
    cur.execute("DELETE from {} WHERE league_id=%s and team_id=%s and level=%s and year=%s".format(sqltable),
                [league.value, team, level.value, get_year_from_season(league, season)])

    url = "http://www.pennantwars.com/viewStats.php?l={}&t={}&level={}&sseason={}&tab={}".format(league,
                                                                                                          team,
                                                                                                          level, season,
                                                                                                          tab)
    if xtype==StatGroup.advanced:
        url += "&xtype=1"

    log("reading " + url)

    html = urllib.request.urlopen(url).read().decode('utf-8', errors='ignore')

    log("making soup")
    soup = BeautifulSoup(html, "lxml")
    table = soup.find("table", "fulltable")

    ## check for missing data (during offseason)
    if table is None:
        return

    p = re.compile(".*p=(\d+).*t=(\d+).*")

    log("massaging data")
    headers = [header.text for header in table.find_all('th')]

    rows = []

    for row in table.find_all('tr', id=False):

        m = p.match(str(row))
        newrow = []
        if m:
            newrow += [str(m.group(1)), str(team), str(int(league)), str(0), str(int(level))]

            for val in row.find_all('td'):
                if val.text == '---':
                    val = newrow.append(str(get_year_from_season(league, season)))
                else:
                    newrow.append(val.text)

            rows.append(newrow)

    # filename = 'stats-{}-{}-{}-{}-{}-{}.csv'.format(league, division, level, season, tab, xtype)
    # log("writing csv to " + filename)
    # with open(filename, 'w') as f:
    #     writer = csv.writer(f)
    #     writer.writerow(headers)
    #     writer.writerows(row for row in rows if row)

    log("writing to database")
    insert_sql = to_insert(sqltable, con)
    #log(insert_sql)
    #log(rows[0])
    cur = con.cursor()
    cur.executemany(insert_sql, rows)


def get_league_date(league):
    url = "http://www.pennantwars.com/league.php?l={}&d=1".format(league)
    log("reading " + url)
    html = urllib.request.urlopen(url).read().decode('utf-8', errors='ignore')

    p = re.compile("<br>(.+?)<br><a href")
    m = p.search(html)
    # log("making soup")
    #soup = BeautifulSoup(html, "lxml")
    #container = soup.find("div", id = "tabcontainer")
    #dates = soup.findAll("div", style ="margin-top:-40px;width:100%;font-weight:bold;text-align:center")
    #d = str(dates[0].string)
    date_object = datetime.datetime.strptime(m.group(1), '%B %d, %Y')
    return date_object.date()


def get_team_activity(league,con):
    cur = con.cursor()
    cur.execute("DELETE from team_activity WHERE league_id=%s", [league.value])

    for division in [1, 2, 3, 4]:
        url = "http://www.pennantwars.com/league.php?l={}&d={}&tab=4".format(league, division)
        log("reading " + url)
        html = urllib.request.urlopen(url).read().decode('utf-8', errors='ignore')
        soup = BeautifulSoup(html, "lxml")
        table = soup.find("table", "fulltable")

        p = re.compile("t=(\d+)")

        activities = []

        for row in table.find_all('tr'):

            m = p.search(str(row))




            if m:
                team_name = row.find('a').text

                team_id = m.group(1)
                tds = [item.text for item in row.find_all('td')]
                last_seen = tds[5]
                conf = tds[0]
                if last_seen == '':
                    continue
                date_object = datetime.datetime.strptime(last_seen, '%m/%d/%y')
                activities.append([league.value, team_id, date_object, team_name, division, conf])
                log("{} {}".format(team_id, last_seen))

        query = "insert into team_activity (league_id, team_id, last_seen, team_name, division, conf) VALUES (%s, %s, %s, %s, %s, %s)"
        cur.executemany(query, activities)


if __name__ == '__main__':

    #con = mysql.connector.connect(host='devbox-me', user='oleepoth', password='urcify', database='pw', port='3316')
    con = mysql.connector.connect(host='localhost', user='root', password='', database='pw')
    con.autocommit = True

    cur = con.cursor()
    cur.execute("SET @@session.sql_mode= ''")

    get_team_schedule(6,19,24, con)
