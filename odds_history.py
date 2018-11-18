__author__ = 'steve'

from pw import *
from odds import postseason_odds
import copy
import operator
import sys
from datetime import timedelta
from datetime import date
from time import strftime
from collections import defaultdict



if __name__ == '__main__':

    con=get_con()
    divisions = list(range(1,5))
    num_sims = 1000

    leagues = [League.mays, League.williams]

    for league in leagues:

        current_year = get_league_date(league).year
        start_year = get_league_start_year(league)
        years = list(range(current_year, start_year - 1, -1))

        for year in years:

            start_date = date(year, 6, 1)
            end_date = date(year, 9, 1)
            day_count = (end_date - start_date).months + 1
            for single_date in (start_date + timedelta(months=n) for n in range(day_count)):
                log(single_date.strftime("%Y-%m-%d"))
                rows = []
                for division in divisions:
                    result = postseason_odds(single_date, num_sims, league.value, division, year, con)
                    for team_id, data in result.items():
                        rows.append([team_id, league.value, year, single_date, data['wins']/num_sims, data['conf']/num_sims, data['unconf']/num_sims, data['wc']/num_sims, data['unwc']/num_sims])
                batch_insert('odds_forecasts', rows, con)