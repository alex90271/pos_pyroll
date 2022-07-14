
#127.0.0.1:5000/
#available data: 
#['tip_rate', 'labor_main', 'labor_rate', 'cout_eod', 'labor_total']
#date format YYYYMMDD (ex. July 4th, 2021 would be represented as: 20210704)

#v01 Routes
from datetime import datetime
from query_db import QueryDB
import flask_weasyprint
from flask import Flask, redirect, render_template, url_for, request, jsonify
from flask_cors import CORS, cross_origin
from report_writer import ReportWriter
from chip_config import ChipConfig

app = Flask(__name__)
cors = CORS(app)
app.config['JSON_SORT_KEYS'] = False
debug = False #set to false to turn off print statements

@cross_origin
@app.route('/v01/data/<day_one>/<day_two>/<rpt_type>/<select_jobs>/<select_emps>')
@app.route('/v01/data/<day_one>/<day_two>/<rpt_type>/<select_jobs>/<select_emps>/<opt_print>/')
def print_rpt(day_one, day_two, rpt_type, select_jobs, select_emps, opt_print='json'):
    if select_emps == '0':
         select_emps = None
    else:
        select_emps = [int(item) for item in select_emps.split(',')]
    if select_jobs == '0':
        select_jobs = None
    else:
        select_jobs = [int(item) for item in select_jobs.split(',')]
    opt_print = str(opt_print).lower()

    if debug:
        print(select_jobs, select_emps)

    result = ReportWriter(day_one, day_two).print_to_json(rpt_type, selected_employees=select_emps, selected_jobs=select_jobs)
    if type(result) == str:
            return jsonify('empty')
    #result.reset_index(drop=True, inplace=True)

    if opt_print == 'json':
        result = result.fillna(0) #turn any NaN data to Zero for json compatability
        result.reset_index(inplace=True)
        return result.to_dict(orient='index')
    elif opt_print == 'html':
        result = result.fillna('') #turn any NaN data to blank for printability
        return render_template('render.html', 
                                tables=[result.to_html(table_id="table", classes="ui striped table")], 
                                titles=result.columns.values,
                                timestamp=datetime.now().strftime('%b %d %Y (%I:%M:%S%p)'),
                                dates=[
                                    datetime.strptime(day_one, "%Y%m%d").strftime('%a, %b %d, %Y'),
                                    datetime.strptime(day_two, "%Y%m%d").strftime('%a, %b %d, %Y')
                                    ],
                                rpttp=rpt_type, 
                                select_emps=select_emps, select_jobs=select_jobs)
    else:
        raise ValueError('Print argument not passed json or html -- leave blank for json')

@app.route('/v01/employees/in_period/<day_one>/<day_two>')
def employees_in_period(day_one, day_two):
    result = ReportWriter(day_one,day_two).employees_in_dates()
    print(result)
    return jsonify(result.to_dict(orient='index'))

@app.route('/v01/print/<day_one>/<day_two>/<rpt_type>/<select_jobs>/<select_emps>')
def print_pdf(day_one, day_two, rpt_type, select_jobs, select_emps, opt_print='html'):
    return flask_weasyprint.render_pdf(url_for(    
                                                'print_rpt',
                                                day_one=day_one,
                                                day_two=day_two,
                                                rpt_type=rpt_type,
                                                select_jobs=select_jobs,
                                                select_emps=select_emps, 
                                                opt_print=opt_print))

@app.route('/v01/config/', methods=["GET"])
def full_config():
    return jsonify(ChipConfig()
    .read_json())

@app.route('/v01/config/<cfg>', methods=["GET"])
def config_item(cfg):
    return jsonify(ChipConfig()
    .query(cfg))

@app.route('/v01/config/<cfg>/<query>', methods=["GET"])
def config_list_item(cfg, query):
    return jsonify(ChipConfig()
    .query(cfg,str(query)))

@app.route('/v01/config/<cfg>/<updated_cfg>')
def config_item_update(cfg,updated_cfg):
    print(updated_cfg)

@app.route('/v01/employees')
def employee_list():
    return jsonify(QueryDB()
    .process_db('employees')
    .to_dict(orient='records'))

@app.route('/v01/jobcodes')
def jobcode_list():
    return jsonify(QueryDB()
    .process_db('jobcodes')
    .to_dict(orient='records'))

@app.route('/v01/reports')
def report_list():
    #return jsonify(['labor_main','labor_total','labor_nightly','tip_rate','labor_rate','cout_eod'])
    return jsonify((
            {'key':'labor_main','text':'labor_main', 'value':'labor_main', 
                "description": '',
                },
            {'key':'labor_total','text':'labor_total','value':'labor_total',
                "description": ''}
               , 
            {'key':'labor_nightly','text':'labor_nightly','value':'labor_nightly',
                "description": '',}
                ,
            {'key':'tip_rate','text':'tip_rate','value':'tip_rate',
                "description": '',}
                ,
            {'key':'labor_rate','text':'labor_rate','value':'labor_rate',
                "description": '',}
                ,
           {'key':'cout_eod','text':'cout_eod','value':'cout_eod',
                "description": '',}
                
        )
        )

#Unfinished Requests
#@app.route('/v01/data/post/<employee_id>/<data>', methods=["POST"])
def update_data(employee_id,data):
    #TODO Finish this. Accepts a json object from frontend {employee_ID : data}
    #data would be adjustments on the worksheet
    pass


if __name__ == '__main__':
    app.run(debug=True)