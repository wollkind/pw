__author__ = 'steve'
import random

from pw import *

if __name__ == '__main__':

    con = get_con()
    con.autocommit = True



    teams = list(range(1,97))
    leagues = [League.mays]

    league_count=0
    total_count=0
    for league in leagues:
        league_count+=1
        log("Starting league {} of {}".format(league_count, len(leagues)))
        current_year = get_league_date(league).year
        start_year = get_league_start_year(league)


        years = list(range(current_year, start_year - 1, -1))
        random.shuffle(years)
        year_count =0
        for year in years:
            year_count+=1
            log("Starting year {} of {}".format(year_count, len(years)))
            season = get_season_from_year(league, year)

            random.shuffle(teams)
            team_count=0
            for team_id in teams:
                team_count+=1
                total_count+=1
                log("Getting team {} of {} ({} of {} total)".format(team_count, len(teams), total_count,
                                                                    len(teams)*len(years)*len(leagues)))
                did_work=get_team_schedule(league, team_id, season, con)
                if did_work:
                    rest()

con.close()
