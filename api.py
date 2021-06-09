
#127.0.0.1:5000/

from query_db import query_db
import timeit
import numpy as np
import sys
import os
import json
import connexion
from flask import jsonify
from gen_rpt import gen_rpt
from datetime import timedelta, date, datetime
from cfg import cfg

first_day = '20210416'
last_day = '20210531'
type = ''

def config():
    return cfg().return_config()

def employees():
    emp_list = query_db(last_day).employee_list()
    emp_json = emp_list.to_json(orient='records')
    return jsonify(emp_json)

def jobcodes():
    job_list = query_db(last_day).jobcode_list()
    job_json = job_list.to_json(orient='records')
    print(job_list, job_json)
    return job_json

def print_rpt():
    return gen_rpt(first_day, last_day).print_to_excel(type)