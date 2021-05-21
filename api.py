
#127.0.0.1:5000/

from query_db import query_db
import timeit
import numpy as np
import sys
import os
from gen_rpt import gen_rpt
from datetime import timedelta, date, datetime
from cfg import cfg
import json
import connexion
from flask import Flask, render_template

app = connexion.App(__name__, specification_dir='./')

# Read the yml file for the endpoints
app.add_api('chip.yml')

def config():
    return cfg().read_json(os.environ['json_name'])

def employees():
    return query_db('20210401').employee_list()

def jobcodes():
    return query_db('20210401').jobcode_list()

def print_rpt(type):
    #TODO implement report printing and specifying the type. 
    pass

def set_date_environ(day_one, day_two):
    os.environ['day_one'] = day_one
    os.environ['day_two'] = day_two
    return day_one, day_two

# if api.py is ran, start the server
if __name__ == '__main__':
    app.run(debug=True)
