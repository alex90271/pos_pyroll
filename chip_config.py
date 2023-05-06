import json
import os
from pathlib import Path
import time


class ChipConfig():

    def __init__(self, config_name='chip.json',pooler_name='pools.json'):
        self.config_name = 'data/'+config_name
        self.pooler_name = 'data/'+pooler_name

        Path('data').mkdir(exist_ok=True)
        Path('debug').mkdir(exist_ok=True)
        Path('exports').mkdir(exist_ok=True)

        path = "exports/"
        now = time.time()

        for filename in os.listdir(path):
            filestamp = os.stat(os.path.join(path, filename)).st_mtime
            filecompare = now - 7 * 86400
            if  filestamp < filecompare:
                print('removing old report: ' + filename)
                os.remove(path + filename)

        if not os.path.isfile(self.config_name):
            print('generating new default config')
            self.save_json(self.generate_config(),self.config_name)

        if not os.path.isfile(self.pooler_name):
            print('generating new default pooler')
            self.save_json(self.generate_pooler(),self.pooler_name)

        self.data = self.read_json(self.config_name)

    def save_json(self, data, name):
        with open(name, 'w') as jsonfile:
            json.dump(data, jsonfile, indent=4)

    def read_json(self,name):
        with open(name) as jsonfile:
            return json.load(jsonfile)

    def generate_config(self):
        '''generates the default config file, with default settings. To reset config file, just delete it'''
        data = {}
        data['ver'] = {'ver': 2}
        data['SETTINGS'] = {
            'tracked_labor': '8',  # array
            'pay_period_days': '15',  # array
            'count_salary': True,  # bool
            'debug': False, #bool
            'verbose_debug': False,  # bool
            'database': 'D:\\Bootdrv\\Aloha\\',  # set to database\ for testing -- str
            'interface_employees': '100, 200, 1002, 1009, 1021, 1022, 9998, 9999', 
            'company_name': ''
        }
    

        return data
    
    def generate_pooler(self):
        '''generates the default pools file, with default settings. To reset config file, just delete it'''
        data = {}
        data['server_pool'] = {
            "contribute": [
                1
            ],
            "receive": [
                2,
                3,
                5,
                10,
                11,
                12,
                13,
                14
            ],
            "type": "sales",
            "percent": "4"
        }
        data['takeout_pool'] = {
            "contribute": [
                4
            ],
            "receive": [
                2,
                3,
                5,
                10,
                11,
                12,
                13,
                14
            ],
            "type": "tips",
            "percent": "100"
        }

        data['luncheon_pool'] = {
            "contribute": [
                40
            ],
            "receive": [
                40
            ],
            "type": "tips",
            "percent": "100"
        }
        return data

    def query(self, config, query=None, return_type='default', updated_result=None):
        '''returns config settings as a string

            Ex. usage for single config settings
            query('database') = 'D:\\Bootdrv\\Aloha\\'

            possible options: 
            register, server, tipout_recip, tip_percent,
            tracked_labor, pay_period, debug, database, and salary'''

        if updated_result:
            self.data[config][query] = updated_result
            self.save_json(self.data)

        if query == None:
            result = self.data[config]
        else:
            result = self.data[config][query]

        # user can specify a return type if necissary.
        if return_type == 'int_array':
            result = [int(x) for x in result.split(',')]
        elif return_type == 'float':
            float(result)
        elif return_type == 'bool':
            bool(result)

        return result


if __name__ == '__main__':
    print("loading ChipConfig.py")
    print(ChipConfig().query("SETTINGS",
          "interface_employees", return_type='int_array'))
