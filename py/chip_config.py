import json
import os


class ChipConfig():

    def __init__(self, json_name='chip.json'):
        self.json_name = 'data/'+json_name

        if not os.path.isfile(self.json_name):
            print('generating new default config')
            try:
                os.mkdir('data')
                os.mkdir('debug')
                os.mkdir('exports')
            except:
                pass
            self.save_json(self.generate_config())

        self.data = self.read_json()

    def save_json(self, data):
        with open(self.json_name, 'w') as jsonfile:
            json.dump(data, jsonfile, indent=4)

    def read_json(self):
        with open(self.json_name) as jsonfile:
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
            'company_name': '',
            'export_type': 'gusto'
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
