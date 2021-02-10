# python -m pip install tkcalendar
# python -m pip install pandas
# python -m pip install dbfread
# python -m pip install xlsxwriter
# python -m pip install python-quickbooks

import pandas as pd 
import datetime
import timeit
from gen_rpt import gen_rpt
import numpy as np

def day_list(
                first_day, 
                last_day, 
                increment = 1
                ):
        '''converts a start date and an end date into a list of all dates in between, based on the increment value'''

        if type(first_day) and type(last_day) == str:
            first_day = datetime.datetime.strptime(first_day, "%Y%m%d")
            last_day = datetime.datetime.strptime(last_day, "%Y%m%d")
        elif type(first_day) or type(last_day) != str or datetime.date:
            raise TypeError('must pass datetime or string')

        delta = datetime.timedelta(days=increment)
        days = []

        while first_day <= last_day:
            cur_day = first_day.strftime("%Y%m%d")
            days.append(cur_day)
            first_day += delta
        
        return days

if __name__ == '__main__':
    print("loading chip.py")

    def main():
        first_day = '20210101'
        last_day = '20210131'
        days = day_list(first_day, last_day)
        rpt = gen_rpt(days)
        print(rpt.tip_rate())

    f = timeit.timeit("main()", "from __main__ import main", number=1)
    print("completed in " + str(np.round(f,2)) + " seconds")


