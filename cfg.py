import configparser
import os

class cfg():

    def __init__(
                self, 
                file_name='chip.ini'
                ):
        self.file_name = file_name
        self.config = configparser.ConfigParser()

    def generate_config (self):
        self.config['DEFAULT'] = {
                            'tip_sales_percent': 0.03,
                            'tip_amt_percent': 100,
                            'percent_sale_codes': 1,
                            'percent_tip_codes': 11, 
                            'tipped_codes': '2,3,5,10,11,12,13,14', 
                            'tracked_labor': 8, 
                            'pay_period_days': 15,
                            'count_salary': True, 
                            'debug': False,
                            'database': 'D:\\Bootdrv\\Aloha\\', # set config.ini to database\ for testing
                            'use_aloha_tipshare': False
                            }
        with open (self.file_name, 'w') as configfile:
            self.config.write(configfile)

    def query (self, query):
        '''returns config settings as a string

            Ex. usage for single config settings
            query('database') = 'D:\\Bootdrv\\Aloha\\'
            
            possible options: 
            register, server, tipout_recip, tip_percent,
            tracked_labor, pay_period, debug, database, and salary'''

        if os.path.isfile(self.file_name):
            self.config.read(self.file_name)
        else:
            print ('generating new ' + self.file_name)
            self.generate_config()

        return self.config.get("DEFAULT", query)

if __name__ == '__main__':
    print("loading cfg.py")
    print(cfg().query('tipped_codes'))