import configparser
import json
import os
from os import path

from numpy import TooHardError

class cfg():

    def __init__(self):
        if os.environ.get('json_name') is None:
            os.environ['json_name'] = 'chip.json'
        self.json_name = os.environ.get('json_name')

        if not os.path.isfile(self.json_name):
            print ('generating new default config')
            self.generate_config()

    def save_json(self, data):
        with open (self.json_name, 'w') as jsonfile:
            json.dump(data, jsonfile, indent=4)
    
    def read_json(self, jsn):
        with open(jsn) as jsonfile:
            return json.load(jsonfile)

    def generate_config (self):
        '''generates the default config file, with default settings. To reset config file, just delete it'''
        data = {}

        data['SETTINGS'] = {
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
        data['RPT_GENERAL'] = {
            'margins_LeftRightTopBottom': [0.5, 0.5, 0.7, 0.7], #margins
            'default_row_width': 20,
            }
        data['RPT_TIP_RATE'] = {
            'col_names': ['Date', 'Tip Hourly', 'Cash Tips', 'Takeout CC Tips', 'Server Tipshare', 'Total Tip Pool', 'Total Tip\'d Hours'],
            'totaled_cols':['Cash Tips', 'Takeout CC Tips', 'Server Tipshare', 'Total Tip Pool', 'Total Tip\'d Hours'], 
            'averaged_cols':['Tip Hourly'], 
            'col_width': 12
            }
        data['RPT_LABOR_RATE'] = {
            'col_names': ['Day', 'Rate (%)','Total Pay', 'Total Sales', 'Reg Hours', 'Over Hours', 'Total Hours'],
            'totaled_cols':['Total Pay', 'Total Sales', 'Reg Hours', 'Over Hours', 'Total Hours'], 
            'averaged_cols':['Rate (%)'], 
            'col_width': 12
            }
        data['RPT_LABOR_MAIN'] = {
            'drop_cols':['RATE', 'TIPSHCON', 'TIP_CONT', 'SALES', 'CCTIPS', 'INHOUR', 'INMINUTE', 'OUTHOUR', 'OUTMINUTE', 'JOBCODE'],
            'index_cols':['LASTNAME', 'FIRSTNAME', 'EMPLOYEE', 'JOB_NAME'],
            'totaled_cols':['HOURS', 'OVERHRS', 'SRVTIPS', 'TIPOUT', 'DECTIPS'],
            'addl_cols':['MEALS'], 
            'col_width': 12
            }
        data['RPT_COUT_EOD'] = {
            'keep_cols_order':['SYSDATEIN', 'EMPLOYEE','FIRSTNAME','LASTNAME', 'JOB_NAME', 'HOURS', 'OVERHRS','INHOUR','INMINUTE', 'OUTHOUR', 'OUTMINUTE', 'COUTBYEOD'],
            'cout_col':'COUTBYEOD', 
            'cout_var':'Y', 
            'col_width': 12
            }
            
        self.save_json(data)
    
    def query (self, config, query, return_type='default'):
        '''returns config settings as a string

            Ex. usage for single config settings
            query('database') = 'D:\\Bootdrv\\Aloha\\'
            
            possible options: 
            register, server, tipout_recip, tip_percent,
            tracked_labor, pay_period, debug, database, and salary'''

        q = self.read_json(self.json_name)[config][query]

        #user can specify a return type if necissary. 
        if return_type == 'int_array':
            q = [int(x) for x in q.split(',')]
        elif return_type == 'float':
            float(q)
        elif return_type == 'bool':
            bool(q)
        
        return q

    def return_config(self):
        return self.read_json(self.json_name)

if __name__ == '__main__':
    print("loading cfg.py")
    print(cfg().return_config())
