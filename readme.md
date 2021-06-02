this is a readme file

python dependencies (updated 5-21-2021)
# python -m pip install tkcalendar
# python -m pip install pandas
# python -m pip install dbfread
# python -m pip install xlsxwriter
# python -m pip install python-quickbooks
# python -m pip install 'connexion[swagger-ui]'
# python -m pip install flask
# python -m pip install json
# python -m pip install jsonformatter

localhost:5000/api/ui

functioning endpoints can be viewed after launching Chip.py and visiting the above link

Currently supports:

GET:
/api/config
    (see cfg.py for example)
/api/employees
    {\"ID\":200,\"FIRSTNAME\":\"Train Server\",\"LASTNAME\":\"Train Register\",\"TERMINATED\":\"N\"}
/api/jobcodes
    {\"ID\":1,\"SHORTNAME\":\"Server\"}
/api/reports/?type='labor_total'
    returns True when the report has been submitted
    options: ['tip_rate', 'labor_main', 'labor_rate', 'cout_eod', 'labor_total']
