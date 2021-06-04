
#127.0.0.1:5000/

from query_db import query_db
import timeit
import numpy as np
import sys
import os
import json
import connexion
from gen_rpt import gen_rpt
from datetime import timedelta, date, datetime
from cfg import cfg

first_day = '20210416'
last_day = '20210531'
type = ''

def set_rpt_params():
    type = connexion.request.headers['type'] #options: ['tip_rate', 'labor_main', 'labor_rate', 'cout_eod', 'labor_total']
    first_day = connexion.request.headers['first_day'] #format YYYYMMDD
    last_day = connexion.request.headers['last_day'] #format YYYYMMDD

def config():
    return cfg().return_config()

def employees():
    emp_list = query_db(last_day).employee_list()
    emp_json = emp_list.to_json(orient='records')
    return emp_json

def jobcodes():
    job_list = query_db(last_day).jobcode_list()
    job_json = job_list.to_json(orient='records')
    return job_json

def print_rpt():
    return gen_rpt(first_day, last_day).print_to_excel(type)