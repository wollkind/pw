__author__ = 'steve'

from pw import *
import copy
import operator
import sys
from collections import defaultdict

def postseason_odds(num_sims, league_id, division, year, con):


    aggregate_results = {}
    aggregate_results = defaultdict(lambda: {'wins':0,'losses':0,'maxwins':0,'maxlosses':0,'conf':0,'unconf':0,'wc':0,'unwc':0}, aggregate_results)

    team_wpcts = get_team_wpcts(league_id, division, year, con)
    team_records = get_team_records(league_id, division, year, con)

    remaining_schedule = get_remaining_schedule(league_id, division, year, con)


    conf1 = get_conf_teams(league_id, division, 1, con)
    conf2 = get_conf_teams(league_id, division, 2, con)
    conf3 = get_conf_teams(league_id, division, 3, con)
    conf4 = get_conf_teams(league_id, division, 4, con)

    for sim in range(1,num_sims+1):
        if sim % 1000 == 0:
            log("Sim number {}".format(sim))
        records_copy = copy.deepcopy(team_records)

        for game in remaining_schedule:
            teamA = game[0]
            teamB = game[1]

            teamA_pct = team_wpcts[teamA]
            teamB_pct = team_wpcts[teamB]

            pA = get_pA(teamA_pct, teamB_pct)

            rand = random.random()
            if rand < pA:
                records_copy[teamA][0]+=1
                records_copy[teamB][1]+=1
            else:
                records_copy[teamA][1]+=1
                records_copy[teamB][0]+=1


        for record in records_copy.items():
            wins = record[1][0]
            losses = record[1][1]

            aggregate_results[record[0]]['wins']+=wins
            aggregate_results[record[0]]['losses']+=losses

            if aggregate_results[record[0]]['maxwins']<wins:
                aggregate_results[record[0]]['maxwins']=wins

            if aggregate_results[record[0]]['maxlosses']<losses:
                aggregate_results[record[0]]['maxlosses']=losses



        c12res = get_half_outcome(records_copy, conf1, conf2)
        c34res = get_half_outcome(records_copy, conf3, conf4)

        aggregate_results[c12res['unwc'][0][0]]['unwc']+=1
        aggregate_results[c12res['unwc'][1][0]]['unwc']+=1
        aggregate_results[c34res['unwc'][0][0]]['unwc']+=1
        aggregate_results[c34res['unwc'][1][0]]['unwc']+=1

        aggregate_results[c12res['wc'][0][0]]['wc']+=1
        aggregate_results[c12res['wc'][1][0]]['wc']+=1
        aggregate_results[c34res['wc'][0][0]]['wc']+=1
        aggregate_results[c34res['wc'][1][0]]['wc']+=1

        aggregate_results[c12res['conf_winners'][0]]['conf']+=1
        aggregate_results[c12res['conf_winners'][1]]['conf']+=1
        aggregate_results[c34res['conf_winners'][0]]['conf']+=1
        aggregate_results[c34res['conf_winners'][1]]['conf']+=1

        aggregate_results[c12res['conf_losers'][0]]['unconf']+=1
        aggregate_results[c12res['conf_losers'][1]]['unconf']+=1
        aggregate_results[c34res['conf_losers'][0]]['unconf']+=1
        aggregate_results[c34res['conf_losers'][1]]['unconf']+=1


    names = get_team_name_dictionary(league_id, division, con)

    sorted_teams = sorted(names.items(), key=operator.itemgetter(1))

    for team in sorted_teams:
        res = aggregate_results[team[0]]

        log("{} releg: {} playoffs: {} conf: {} wc: {}".format(team[1], (res['unwc']+res['unconf'])/num_sims*100, (res['wc']+res['conf'])/num_sims*100,res['conf']/num_sims*100,res['wc']/num_sims*100 ))

    return aggregate_results

def get_team_name_dictionary(league_id, division, con):
    cur = con.cursor()
    cur.execute("""select team_id, team_name from team_activity where division=%s and league_id=%s""",[division, league_id])

    ret={}
    result=cur.fetchall()
    for row in result:
        ret[row[0]]=row[1]

    return ret

def get_conf_teams(league_id, division, conf_id, con):
    cur = con.cursor()
    cur.execute("""select team_id from team_activity where division=%s and league_id=%s and conf=%s""",[division, league_id, conf_id])

    output = []

    result = cur.fetchall()
    for row in result:
        output += [row[0]]

    return output

def get_playoff_outcome(records, conf1, conf2, conf3, conf4):

    get_conf_outcomes(records, conf)

def get_conf_outcomes(records, teams):
    conf_records={team: records[team] for team in teams}
    sorted_teams = sorted(conf_records.items(), key=operator.itemgetter(1), reverse=True)

    winner = sorted_teams[0]
    loser = sorted_teams[5]

    return [winner[0], loser[0]]

def get_half_outcome(records, teams1, teams2):
    c1result = get_conf_outcomes(records, teams1)
    c2result = get_conf_outcomes(records, teams2)

    half_records = {team: records[team] for team in teams1+teams2}

    for team in c1result+c2result:
        del half_records[team]

    sorted_teams = sorted(half_records.items(), key=operator.itemgetter(1), reverse=True)


    wc = [sorted_teams[x] for x in [0,1]]
    unwc = [sorted_teams[x] for x in [6,7]]

    return {'conf_winners': [c1result[0], c2result[0]], 'conf_losers': [c1result[1], c2result[1]], 'wc': wc, 'unwc': unwc}

def get_pA(wpct1, wpct2):
    p1 = (wpct1 - wpct1 * wpct2)/(wpct1+wpct2-2*wpct1*wpct2)
    return p1

def get_team_records(league_id, division, year, con):
    cur = con.cursor()
    cur.execute("""select s.team_id, sum(case when result='W' then 1 else 0 end)+(sum(rs)-sum(ra))/count(*)/100, sum(case when result='L' then 1 else 0 end) from schedule_and_results s, team_activity a where a.team_id=s.team_id and
    a.division=%s and s.year=%s and a.league_id=s.league_id and a.league_id=%s group by s.team_id""",[division, year, league_id])

    result = cur.fetchall()

    team_records = {}

    for row in result:
        team_records[row[0]]=[row[1], row[2]]

    return team_records

def get_team_wpcts(league_id, division, year, con):

    cur = con.cursor()
    cur.execute("""select s.team_id, sum(RS), sum(RA) from schedule_and_results s, team_activity a where a.team_id=s.team_id and
    a.division=%s and s.year=%s and a.league_id=s.league_id and a.league_id=%s group by s.team_id""",[division, year, league_id])

    result = cur.fetchall()

    team_wptcs = {}

    for row in result:
        team_wptcs[row[0]]=row[1]**2/(row[1]**2+row[2]**2)


    return team_wptcs

def get_remaining_schedule(league_id, division, year, con):

    cur = con.cursor()
    cur.execute("""select s.team_id, s.opponent_id from schedule_and_results s, team_activity a where a.team_id=s.team_id and
    a.division=%s and s.year=%s and a.league_id=s.league_id and a.league_id=%s and s.team_id<opponent_id and result is null""",[division, year, league_id])

    result = cur.fetchall()
    return result

if __name__ == '__main__':

    con=get_con()
    division = int(sys.argv[1])
    num_sims = int(sys.argv[2])
    current_year = get_league_date(6).year

    res = postseason_odds(num_sims, 6, division, current_year, con)


