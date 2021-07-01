this is a readme file

python dependencies (updated 7-1-2021)
# python -m pip install pandas
# python -m pip install dbfread
# python -m pip install xlsxwriter
# python -m pip install flask

built on python 3.8.6 64Bit

run chip_api.py to launch

localhost:5000

functioning endpoints can be viewed after launching Chip.py and visiting the above link

Currently supports:


GET:
/v01/print/<day_one>/<day_two>/<rpt_type>
    returns True when the report has been submitted
    options: ['tip_rate', 'labor_main', 'labor_rate', 'cout_eod', 'labor_total']
/v01/view/<day_one>/<day_two>/<rpt_type>
    same as the above, except returns raw data
    same options as above

/v01/config/
    returns the ENTIRE config as a json object
v/01/config/<query>
    returns a config item. see cfg.py for more details


