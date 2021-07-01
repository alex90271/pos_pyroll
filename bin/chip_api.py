
#127.0.0.1:5000/

from query_db import query_db
import numpy as np
import os
from flask import Flask, redirect, url_for, request, jsonify
from gen_rpt import gen_rpt
from cfg import cfg

app = Flask(__name__)

#available data: 
#['tip_rate', 'labor_main', 'labor_rate', 'cout_eod', 'labor_total']

#v01 Routes
@app.route('/v01/print/<day_one>/<day_two>/<rpt_type>', methods=["GET"])
def print_rpt(day_one, day_two, rpt_type):
    return gen_rpt(day_one, day_two).print_to_excel(rpt_type)

@app.route('/v01/view/<day_one>/<day_two>/<data_type>', methods=["GET"])
def data_viewer(day_one, day_two, type):
    if type in list(['tip_rate', 'labor_main', 'labor_rate', 'cout_eod', 'labor_total']): 
        rpt = gen_rpt(day_one, day_two)
        rpt.print_to_excel(str(type))

@app.route('/v01/data/post/<employee_id>/<data>', methods=["POST"])
def update_data(employee_id,data):
    #TODO Finish this. Accepts a json object from frontend {employee_ID : data}
    #data would be adjustments on the worksheet
    return 'congrats. it ran.'

@app.route('/v01/config/', methods=["GET"])
def full_config():
    return cfg().read_json(os.environ.get('json_name'))

@app.route('/v01/config/<query>', methods=["GET"])
def config_item(query):
    return jsonify(cfg().query('SETTINGS',str(query)))


@app.route('/v01/employee')
def employee_list():
    return query_db().process_db('employees')

@app.route('/v01/jobcodes')
def jobcode_list():
    return query_db().process_db('jobcodes')




if __name__ == '__main__':
    app.run(debug=True)