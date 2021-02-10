from process_labor import process_labor as labor
from process_tips import process_tips as tips
import numpy as np
import pandas as pd
import datetime

class gen_rpt():

    def __init__(self, first_day, last_day=None, increment=1):
        self.first_day = first_day
        self.last_day = last_day
        self.days = []

        if last_day == None:
            self.days.append(first_day)
        else: 
            if type(first_day) and type(last_day) == str:
                first_day = datetime.datetime.strptime(first_day, "%Y%m%d")
                last_day = datetime.datetime.strptime(last_day, "%Y%m%d")
            elif type(first_day) or type(last_day) != str or datetime.date:
                raise TypeError('must pass datetime or string')

            while first_day <= last_day:
                cur_day = first_day.strftime("%Y%m%d")
                self.days.append(cur_day)
                first_day += datetime.timedelta(days=increment)

    def tip_rate(self):
        #print('\n\nday ' + str(day) + '\n\n')
        t = [tips(day).calc_tiprate_df() for day in self.days]
        return pd.concat(t)

    def labor_rate(self):
        l = [labor(day).calc_laborrate_df() for day in self.days]
        return pd.concat(l)

    #concatenates the data
    def labor_main(
                    self, 
                    debug=False
                    ): 
        a = [tips(day).calc_all_tips() for day in self.days]
        df = pd.concat(a)
        if not debug:
            _df = df.pivot_table(df, index=['LASTNAME', 'FIRSTNAME','JOB_NAME'], aggfunc=np.sum, fill_value=np.NaN)
            _df = _df[['HOURS', 'OVERHRS', 'SRVTIPS', 'TIPOUT', 'DECTIPS']]
            _df.loc[:,('MEALS')] = np.nan

        return _df

if __name__ == '__main__':
    print("loading gen_rpt.py")
    print(gen_rpt('20210101','20210115').tip_rate())