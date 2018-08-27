__author__ = 'steve'

from bs4 import BeautifulSoup
import urllib.request
import mysql.connector
import csv
import re
import ssl
import random
import itertools
from io import StringIO
import socket
import datetime
from enum import IntEnum
from time import sleep


class League(IntEnum):
    mays = 6
    williams = 5




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
    if league==League.williams:
        return 2013
    else:
        return 2014


def get_con():

    host = socket.gethostname()
    if host=="stevens-mbp.home":
        return mysql.connector.connect(host='li1281-193.members.linode.com', user='njord', password='r905pyc', database='pw')
    else:
        return mysql.connector.connect(host='steve-pw.cvyzuxuyy5fs.us-east-2.rds.amazonaws.com', user='root', password='timA&Mpw9', database='pw')



def log(message):
    print("[{}] {}".format(datetime.datetime.now(), message))


def rest():
    sleeptime = 1
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

def get_html(url):
    log("...reading " + url)
    gcontext = ssl.SSLContext(ssl.PROTOCOL_TLSv1)  # Only for gangsters
    html = urllib.request.urlopen(url, context=gcontext).read().decode('utf-8', errors='ignore')
    return html

def get_soup(url):
    html = get_html(url)
    log("...making soup")
    soup = BeautifulSoup(html, "lxml")
    return soup


def batch_insert(table, rows, con):
    log("...writing to database")
    cur = con.cursor()
    query_string = to_insert(table, con)
    cur.executemany(query_string, rows)
    con.commit()


def get_team_history(league, team_id, con):
    cur = con.cursor()
    cur.execute("DELETE from team_histories where team_id=%s and league_id=%s", [team_id, league.value])

    url = "http://www.pennantwars.com/team.php?l={}&t={}&tab=4&x=1".format(league, team_id)
    soup = get_soup(url)
    table = soup.find_all("table", "fulltable")[3]
    log(table)
    rows=[]

    for row in table.find_all('tr', attrs={'id': None}):
        vals = row.find_all('td')
        res = [x.text.split(" - ") for x in vals]
        res = list(itertools.chain.from_iterable(res))
        res.append(team_id)
        res.append(league.value)
        rows.append(res)


    batch_insert('team_histories', rows, con)


def get_sign_now(league, pos, con):
    cur = con.cursor()
    cur.execute("DELETE from sign_nows WHERE pos=%s and league_id=%s", [pos,league.value])

    url = "http://www.pennantwars.com/freeAgents.php?l={}&pos={}".format(league, pos)
    soup = get_soup(url)
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

    batch_insert('sign_nows',rows,con)


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

    html = get_html(url)

    log("replacing DL")
    html = html.replace("<span style='font-weight:bold;color:rgb(180, 47, 47)'>DL</div>", "DL")

    log("writing csv")
    with open("players-{}-{}-{}".format(league, year, h), "w") as text_file:
         text_file.write(html)

    f = StringIO(html)

    log("converting to csv")
    reader = csv.reader(f)
    your_list = list(reader)
    log("...massaging data")

    newrows = [[league.value, str(year)] + [None if not x else x for x in row] for row in your_list[1:]]

    batch_insert(table,newrows,con)


def get_team_news(league, team, season, con):
    year = get_year_from_season(league, season)

    url = "http://www.pennantwars.com/team.php?l={}&t={}&tab=3&xseason={}".format(league.value, team,season)
    get_soup(url)
    transactions = soup.find("table", class_="fulltable noStretch").find_all("tr")

    for trans in transactions:
        log(trans.text)

    log("done")


def get_team_schedule(league, team, season, con):
    ## delete this set of rows from games table
    year = get_year_from_season(league, season)

    cur = con.cursor()
    # cur.execute("DELETE from schedule_and_results WHERE league_id=%s and team_id=%s and year=%s",
    #             [league.value, team, year])

    cur.execute("SELECT count(*) c from schedule_and_results WHERE league_id=%s and team_id=%s and year=%s and result is not null",
                [league.value, team, year])

    numrows = int(cur.fetchone()[0])
    if numrows >= 162:
        log("No work to do")
        return False

    cur.execute("DELETE from schedule_and_results WHERE league_id=%s and team_id=%s and year=%s",
                [league.value, team, get_year_from_season(league, season)])

    url = "http://www.pennantwars.com/team.php?l={}&t={}&tab=2&xseason={}".format(league.value, team,season)
    log("...reading "+url)
    html = urllib.request.urlopen(url).read().decode('utf-8', errors='ignore')

    log("...making soup")
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

            game_link = cells[1].text
            if "@" in game_link:

                home=False
            else:
                home = True

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
                    awayruns=resm.group(2)
                    homeruns=resm.group(3)

                    if home:
                        rs=homeruns
                        ra=awayruns
                    else:
                        rs=awayruns
                        ra=homeruns

                newrow = [league.value, team, year, str(strdate), game, str(opponent), result_char, rs, ra]
                result_rows.append(newrow)

    log(result_rows[2])
    batch_insert('schedule_and_results', result_rows, con)
    return True


def get_pw_stats(league, team, level, season, tab, xtype, con, reload=False):
    log("Getting {} {} {} {} {} {}".format(league, team, level, season, tab, xtype))
    if tab == StatType.fielding:
        sqltable = 'fielding_stats'
        skip_columns = []
    elif tab == StatType.hitting:
        if xtype == StatGroup.basic:
            sqltable = 'hitting_stats'
            skip_columns = [2,3,4]
        else:
            sqltable = 'adv_hitting_stats'
            skip_columns = [2,3,4]
    elif tab == StatType.pitching:
        if xtype == StatGroup.basic:
            sqltable = 'pitching_stats'
            skip_columns = [2,3,4]
        else:
            sqltable = 'adv_pitching_stats'
            skip_columns = [2,3,4]

    cur = con.cursor()
    # cur.execute("DELETE from {} WHERE league_id=%s and team_id=%s and level=%s and year=%s".format(sqltable),
    #             [league.value, team, level.value, get_year_from_season(league, season)])

    cur.execute("SELECT count(*) numrows from {} WHERE league_id=%s and team_id=%s and level=%s and year=%s".format(sqltable),
                [league.value, team, level.value, get_year_from_season(league, season)])

    numrows = int(cur.fetchone()[0])

    if int(numrows) > 0 and reload is False:
        log("No work to do")
        return False
    else:
        cur.execute("DELETE from {} WHERE league_id=%s and team_id=%s and level=%s and year=%s".format(sqltable),
                [league.value, team, level.value, get_year_from_season(league, season)])


    url = "http://www.pennantwars.com/viewStats.php?l={}&t={}&level={}&sseason={}&tab={}".format(league,
                                                                                                          team,
                                                                                                          level, season,
                                                                                                          tab)
    if xtype==StatGroup.advanced:
        url += "&xtype=1"

    soup = get_soup(url)
    table = soup.find("table", "fulltable")

    ## check for missing data (during offseason)
    if table is None:
        log("...no stats")
        return True

    p = re.compile(".*p=(\d+).*t=(\d+).*")

    log("...massaging data")


    rows = []

    for row in table.find_all('tr', id=False):

        m = p.match(str(row))
        newrow = []
        if m:
            newrow += [str(m.group(1)), str(team), str(int(league)), str(int(level))]
            column_no = 0
            for val in row.find_all('td'):
                column_no += 1
                if column_no in skip_columns:
                    next
                elif val.text == '---':
                    newrow.append(str(get_year_from_season(league, season)))
                else:
                    newrow.append(val.text)
            if newrow[4] != "Average":
                rows.append(newrow)
                #log(newrow)


    batch_insert(sqltable, rows, con)
    return True


def get_league_date(league):
    url = "http://www.pennantwars.com/league.php?l={}&d=1".format(league)
    html = get_html(url)

    p = re.compile("<br>(.+?)<br><a href")
    m = p.search(html)
    # log("...making soup")
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
        soup = get_soup(url)
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
                activities.append([team_id, league.value, date_object, team_name, division, conf])


        batch_insert('team_activity', activities, con)



def get_all_stats_for_league_year(league, year, teams, levels, types, con, reload=False):
    season = get_season_from_year(league, year)
    random.shuffle(teams)
    team_count = 0
    for team_id in teams:
        team_count+=1
        log("Starting {} {} {} ({} of {})".format(league.name, year, team_id, team_count, len(teams)))
        random.shuffle(levels)

        level_count = 0

        for level in levels:
            level_count+=1
            log("Starting {} {} {} {} ({} of {})".format(league.name, year, team_id, level, level_count, len(levels)))
            random.shuffle(types)
            for type in types:
                did_work = get_pw_stats(league, team_id, level, season, type, StatGroup.basic, con, reload)
                if did_work:
                    rest()
                did_work = get_pw_stats(league, team_id, level, season, type, StatGroup.advanced, con, reload)
                if did_work:
                    rest()
        #did_work = get_pw_stats(league, team_id, Level.ml, season, StatType.fielding, StatGroup.basic, con, reload)
        # if did_work:
        #     rest()



if __name__ == '__main__':

    con = get_con()

    cur = con.cursor()
    cur.execute("SET @@session.sql_mode= ''")
    get_sign_now(League.mays, 0, con)
    #get_pw_stats(League.mays, 20, Level.ml, 23, StatType.hitting, StatGroup.basic, con)
    #get_team_news(League.mays, 19, 22, con)
    #get_team_history(League.mays, 20, con)
    #get_team_activity(League.mays, con)
