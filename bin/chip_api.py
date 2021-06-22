
#127.0.0.1:5000/

from query_db import query_db
import numpy as np
import os
import json
from flask import Flask, redirect, url_for, request
from gen_rpt import gen_rpt
from cfg import cfg

app = Flask(__name__)

@app.route('/v01/print/<day_one>')
def print_rpt(day_one):
    return gen_rpt(day_one).print_to_excel('labor_main')

if __name__ == '__main__':
    app.run(debug=True)