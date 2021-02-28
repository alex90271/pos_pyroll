import configparser
import json
import os

class cfg():

    def __init__(
                self, 
                file_name='chip.json'
                ):
        self.file_name = file_name
        self.data = {}

    def generate_config (self):
        '''generates the default config file, with default settings. To reset config file, just delete it'''
        self.data['SETTINGS'] = {
            'tip_sales_percent': '0.03', #float, 0 - 1 (decimal percent)
            'tip_amt_percent': '1', #float, 0 - 1 (decimal percent)
            'percent_sale_codes': '1', #array
            'percent_tip_codes': '11', #array
            'tipped_codes': '2,3,5,10,11,12,13,14', #array
            'tracked_labor': '8', #array
            'pay_period_days': '15', #array
            'count_salary': True, #bool
            'debug': False, #bool
            'database': 'D:\\Bootdrv\\Aloha\\', # set to database\ for testing -- str
            'use_aloha_tipshare': False #bool
            }
        self.data['RPT_TIP_RATE'] = {
            'col_names': ['Date', 'Tip Hourly', 'Cash Tips', 'Takeout CC Tips', 'Server Tipshare', 'Total Tip Pool', 'Total Tip\'d Hours'],
            'totaled_cols':['Cash Tips', 'Takeout CC Tips', 'Server Tipshare', 'Total Tip Pool', 'Total Tip\'d Hours'], 
            'averaged_cols':['Tip Hourly']
            }
        self.data['RPT_LABOR_RATE'] = {
            'col_names': ['Day', 'Rate (%)','Total Pay', 'Total Sales', 'Reg Hours', 'Over Hours', 'Total Hours'],
            'totaled_cols':['Total Pay', 'Total Sales', 'Reg Hours', 'Over Hours', 'Total Hours'], 
            'averaged_cols':['Rate (%)']
            }
        self.data['RPT_LABOR_MAIN'] = {
            'drop_cols':['RATE', 'TIPSHCON', 'TIP_CONT', 'SALES', 'CCTIPS', 'INHOUR', 'INMINUTE', 'OUTHOUR', 'OUTMINUTE', 'JOBCODE'],
            'index_cols':['LASTNAME', 'FIRSTNAME', 'EMPLOYEE', 'JOB_NAME'],
            'totaled_cols':['HOURS', 'OVERHRS', 'SRVTIPS', 'TIPOUT', 'DECTIPS'],
            'addl_cols':['MEALS']
            }
        self.data['RPT_COUT_EOD'] = {
            'keep_cols_order':['SYSDATEIN', 'EMPLOYEE','FIRSTNAME','LASTNAME', 'JOB_NAME', 'HOURS', 'OVERHRS','INHOUR','INMINUTE', 'OUTHOUR', 'OUTMINUTE', 'COUTBYEOD'],
            'cout_col':'COUTBYEOD', 
            'cout_var':'Y'
            }
        with open (self.file_name, 'w') as jsonfile:
            json.dump(self.data, jsonfile, indent=4)

    def query (self, query, config='SETTINGS'):
        '''returns config settings as a string

            Ex. usage for single config settings
            query('database') = 'D:\\Bootdrv\\Aloha\\'
            
            possible options: 
            register, server, tipout_recip, tip_percent,
            tracked_labor, pay_period, debug, database, and salary'''

        if not os.path.isfile(self.file_name):
            print ('generating new ' + self.file_name)
            self.generate_config()

        with open(self.file_name) as jsonfile:
            self.data = json.load(jsonfile) 

        return self.data[config][query]

if __name__ == '__main__':
    print("loading cfg.py")
    a = cfg().query('database')
    print(a)
