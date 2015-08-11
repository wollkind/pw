__author__ = 'steve'

from pw import *

if __name__ == '__main__':

    #con = mysql.connector.connect(host='devbox-me', user='oleepoth', password='urcify', database='pw', port='3316')
    con = mysql.connector.connect(host='localhost', user='root', password='', database='pw')
    con.autocommit = True

    log("Cleaning stat tables")
    cur = con.cursor()
    cur.execute("SET @@session.sql_mode= ''")
    cur.execute("truncate adv_hitting_stats")
    cur.execute("truncate adv_pitching_stats")
    cur.execute("truncate hitting_stats")
    cur.execute("truncate pitching_stats")
    cur.execute("truncate fielding_stats")

    for league in [League.foxx]:
        log("Backfilling {}".format(league.name))
        for level in [Level.aaa, Level.ml, Level.lm]:
            log("Doing level {}".format(level))
            for type in [StatType.hitting, StatType.pitching]:
                log("Doing stattype {}".format(type))
                if level != Level.ml:
                    if type == StatType.fielding:
                        log("Skipping")
                        continue
                    divisions = range(0,1)
                else:
                    divisions = range(1,5)

                for division in divisions:
                    log("Backfilling division {} level {} type {} basic".format(division, level.name, type.name))
                    get_pw_stats(league,division,level,-1,type,StatGroup.basic, con)

                    rest()
                    if type != StatType.fielding:
                        log("Backfilling division {} level {} type {} advanced".format(division, level.name, type.name))
                        get_pw_stats(league,division,level,-1,type,StatGroup.advanced, con)
                        rest()

    con.close()