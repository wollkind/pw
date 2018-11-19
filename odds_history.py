__author__ = 'steve'

from pw import *
from odds import postseason_odds
import copy
import operator
import sys
from dateutil.relativedelta import *
from datetime import timedelta
from datetime import date
from time import strftime
from collections import defaultdict



if __name__ == '__main__':

    con=get_con()
    divisions = list(range(1,5))
    num_sims = 1000
    cur = con.cursor()

    leagues = [League.mays, League.williams]

    for league in leagues:

        current_year = get_league_date(league).year
        start_year = get_league_start_year(league)
        years = list(range(current_year, start_year - 1, -1))

        for year in years:

            start_date = date(year, 9, 1)
            end_date = date(year, 9, 26)
            day_count = (end_date - start_date).days + 1
            for single_date in (start_date + timedelta(n) for n in range(day_count)):
                single_date = single_date.strftime("%Y-%m-%d")

                cur.execute(
                    "SELECT count(*) numrows from odds_forecasts WHERE league_id=%s and date=%s",
                    [league.value, single_date])

                numrows = int(cur.fetchone()[0])

                if int(numrows) == 96:
                    log("No work to do for {} league {}".format(single_date, league.name))
                else:
                    log(single_date)
                    cur.execute(
                        "DELETE from odds_forecasts WHERE league_id=%s and date=%s",
                        [league.value, single_date])
                    rows = []
                    for division in divisions:
                        result = postseason_odds(single_date, num_sims, league.value, division, year, con)
                        for team_id, data in result.items():
                            rows.append([team_id, league.value, year, single_date, data['wins']/num_sims, data['conf']/num_sims, data['unconf']/num_sims, data['wc']/num_sims, data['unwc']/num_sims])

                    batch_insert('odds_forecasts', rows, con)