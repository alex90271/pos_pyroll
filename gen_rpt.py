from process_labor import process_labor as labor
from process_tips import process_tips as tips
import numpy as np
import pandas as pd

class gen_rpt():

    def __init__(self, days):
        self.days = days

    def tip_rate(self):
        a = []
        for day in self.days:
            print('\n\nday ' + str(day) + '\n\n')
            t = tips(day)
            a.append(
                pd.DataFrame(data={
                    'Date': [t.get_day()], 
                    'Tipped Hours': [round(t.get_tipped_hours(),2)], 
                    'Server Tipshare': [round(t.get_percent_sales(),2)], 
                    'Takeout Pool': [round(t.get_percent_tips(),2)], 
                    'Rate': [round(t.get_tip_rate(),2)],
                    #TODO finish
                }))

        return pd.concat(a)


    def labor_rate(self):
        a = []
        for day in self.days:
            print('\n\nday ' + str(day) + '\n\n')
            l = labor(day)
            a.append(
                pd.DataFrame(data={
                    'day': [l.get_day()],
                    'rate': [np.round(l.get_labor_rate(),2)]
            }))

        return pd.concat(a)

    #concatenates the data
    def labor_main(
                    self, 
                    debug=False
                    ): 
        a = []
        for day in self.days:
            #print('\n\nday ' + str(day) + '\n\n')
            t = tips(day)
            a.append(t.calc_all_tips())
        df = pd.concat(a)
        if not debug:
            _df = df.pivot_table(df, index=['LASTNAME', 'FIRSTNAME','JOB_NAME'], aggfunc=np.sum, fill_value=np.NaN)
            _df = _df[['HOURS', 'OVERHRS', 'SRVTIPS', 'TIPOUT', 'DECTIPS']]
            _df.loc[:,('MEALS')] = np.nan

        return _df

if __name__ == '__main__':
    print("loading gen_rpt.py")
    print(gen_rpt(["20210109"]).tip_rate())