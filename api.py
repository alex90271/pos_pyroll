
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
    return jsonify(emp_list)

def jobcodes():
    job_list = query_db(last_day).jobcode_list()
    return jsonify(job_list)



def print_rpt():
    return gen_rpt(first_day, last_day).print_to_excel(type)