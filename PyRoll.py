#required installs 
# python -m pip install tkcalendar
# python -m pip install pandas
# python -m pip install dbfread
# python -m pip install xlsxwriter

# python -m pip install python-quickbooks -- https://pypi.org/project/python-quickbooks/

print('...app starting, please wait...\n')

import subprocess
import csv
import sys
import datetime
import os
import dbfread
import pandas as pd
import tkinter as tk
import numpy as np
import configparser
import pandas.io.excel._xlsxwriter
import glob
import calendar
import xlsxwriter
import sys
from babel.dates import format_date, parse_date, get_day_names, get_month_names
from babel.numbers import *
from os import path
from datetime import date, time, timedelta
from tkinter import *
from tkcalendar import *
from dbfread import DBF

#config stuff
config = configparser.ConfigParser()
def generateconfig ():
    config['DEFAULT'] = {'tip share percent': 0.03, 'databaseloc': 'D:\\Bootdrv\\Aloha\\', 'server jobcode number': '1',
                        'take out reg job code number': '11', 'jobcode numbers to receive tips': '2,3,5,10,11,12,13,14',
                        'debug': False, 'labor report jobcodes': '8', 'salary': True, 'payroll days': 15}
    with open ('config.ini', 'w') as configfile:
        config.write(configfile)

def grabItem(df, column, row):
    '''assumes you pass a pandas dataframe'''
    pass

#generate folders
if os.path.isfile('config.ini'):
    print ('using existing config')
    config.read('config.ini')
else:
    print ('generating new config')
    generateconfig()
try:
    os.mkdir('output')
except FileExistsError:
    pass
try:
    os.mkdir('csv')
except FileExistsError:
    pass

#global variables
databaseloc = config.get("DEFAULT", "databaseloc")
qtoday = datetime.datetime.now()
thedict = []

#convert dbf to csv
def processdatabase (dayofreport):
    '''when function is given a date, it will look for the database location of aloha, find the database files and process them into a readable csv'''

    labor = DBF(databaseloc + dayofreport + '/ADJTIME.DBF')
    counter = 0
    with open('csv/'+ dayofreport +'_labor.csv','w', newline='') as lbrexport:
        writer = csv.writer(lbrexport, delimiter=',')
        writer.writerow(labor.field_names)
        for row in labor:
            writer.writerow(list(row.values()))
            counter += 1
        if counter == 0:
            #writes in a fake shift is the data is empty-- pandas cannot parse empty csvs, but we still need the date in the data
            writer.writerow(list([9999,0,'N',0,datetime.datetime.strptime(dayofreport,'%Y%m%d'),datetime.datetime.strptime(dayofreport,'%Y%m%d'),datetime.datetime.strptime(dayofreport,'%Y%m%d'),4,5,00,5,00,0,0,0.0,0.0,0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0,0,0.0,0.0,0,0.0,0.0,'N','N',0,0.0,0.0,0,0.0,0.0,1,1,1,0,0,0,0,0.0,0.0,0.0,0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0,0,0.0,0.0,0.0,0,0,0.0,0.0,0,'00:00:00',0,0,0,0,0,0.0,0.0,0.0,0.0,'N','N',0,'N']))
        #print(counter)
            
    #jobcode numbers
    jobcode = DBF(databaseloc + dayofreport + '/JOB.Dbf')
    with open('csv/'+ dayofreport +'_jobcode.csv','w', newline='') as jobcodeexport:
        writer = csv.writer(jobcodeexport, delimiter=',')
        writer.writerow(jobcode.field_names) 
        for row in jobcode:
            writer.writerow(list(row.values()))

    #employee names
    employee = DBF(databaseloc + dayofreport + '/EMP.DBF', char_decode_errors='ignore')
    with open('csv/'+ dayofreport +'_employee.csv','w', newline='') as employeeexport:
        writer = csv.writer(employeeexport, delimiter=',')
        writer.writerow(employee.field_names)
        for record in employee:
            writer.writerow(list(record.values()))

    #https://pandas.pydata.org/docs/user_guide/io.html#io-read-csv-table

    #collects sales, tips, and hours data from aloha. Data does not include jobcode names or employee names, jobcode.csv and employee.csv contain this information
    laborpd = pd.read_csv('csv/'+ dayofreport +'_labor.csv', usecols=['SYSDATEIN','INVALID','JOBCODE','EMPLOYEE','HOURS','OVERHRS','CCTIPS','DECTIPS','COUTBYEOD','SALES','INHOUR','INMINUTE','OUTHOUR','OUTMINUTE','RATE', 'SALES'])
    laborpd = laborpd.loc[(laborpd['INVALID']=="N")]
    #jobcode names
    jobcodepd = pd.read_csv('csv/'+ dayofreport +'_jobcode.csv', usecols=['ID','SHORTNAME'])
    jobcodepd = jobcodepd.rename(columns={'ID': 'JOBCODE'})
    jobcodepd = jobcodepd.rename(columns={'SHORTNAME': 'JOB_NAME'})

    #employee names
    employeepd = pd.read_csv('csv/'+ dayofreport +'_employee.csv', usecols=['ID','LASTNAME','FIRSTNAME', 'TERMINATED',])
    employeepd = employeepd.loc[(employeepd['TERMINATED']=="N")]
    employeepd = employeepd.rename(columns={'ID':'EMPLOYEE'})

    #merge employee names, jobcode names, sales data, and hours worked onto one csv file
    labordata = laborpd.merge(employeepd, on='EMPLOYEE')
    labordata = labordata.merge(jobcodepd, on='JOBCODE')
    #labordata = labordata.drop(0, axis=0)
    labordata.to_csv('csv/'+ dayofreport +'_labordata.csv')
    
    print("report data for " + dayofreport + " was successfully compiled")

def salesZero(tltsales, tltpay):
    if tltsales == 0:
        return 0
    else:
        return (tltpay/tltsales * 100)

#calculate tips
def processtips (day):
    '''this function assumes a data grind has already been run. runs over the date its given and calculates the tips and overwrites previous data'''
    file_name = 'csv/'+ day +'_labordata.csv'

    salaried = pd.read_csv('salary.csv')
    jobs = pd.read_csv('csv/'+ day +'_jobcode.csv')

    #config options
    takeout_reg = str(config.get("DEFAULT", "take out reg job code number")).split(',')
    server_jobcode = str(config.get("DEFAULT", "server jobcode number")).split(',')
    tipout_recip = str(config.get("DEFAULT", "jobcode numbers to receive tips")).split(',')
    tipshare_percent = float(config.get("DEFAULT", "tip share percent"))
    labor_jobcode = str(config.get("DEFAULT", "labor report jobcodes")).split(',')
    payroll_days = float(config.get("DEFAULT", "payroll days"))

    iterative_keys = ['HOURS', 'OVERHRS', 'CCTIPS', 'DECTIPS', 'SALES', 'SRVTIPS', 'TIPOUT', 'RATE', 'SALES']

    working_dict = []
    #jobcodes - 1:Server, 2:Assist/Bus, 5:Bar/Dessert, 6:Shag, 7:Dish, 8:Fry Cook, 9:Kitchen, 11:Register, 13:Pay/Phones, 14:Bagger, 50:Manager
    #process labordata into a dict object, and turn iterative keys above into floats vs strings
    with open(file_name) as labordata:
        labordata = csv.DictReader(labordata)
        working_dict = []
        server_tipshrpool = 0
        to_cctips = 0
        reg_cash = 0
        for item in labordata:
            working_dict.append(item)
            for item in working_dict:
                for key in item:
                    if key in iterative_keys:
                        item[key] = float(item[key])
        
        #Calculates tips and tipouts
        tltsales = 0
        tltpay = 0
        tlt_reg_hour = 0
        tlt_over_hours = 0
        for item in working_dict:
            server_tips = 0
            hrs = 0
            tipshare = 0
            if float(item["OVERHRS"]) > 0:
                hrs = float(item["HOURS"]) - float(item["OVERHRS"])
                item.update({"HOURS": hrs})
            if item["JOBCODE"] in server_jobcode:
                tipshare = float(item['SALES']) * tipshare_percent
                server_tips = float(item['CCTIPS']) - tipshare
            if item["JOBCODE"] in takeout_reg:
                tipshare = float(item['CCTIPS'])
                to_cctips += float(item['CCTIPS'])
            if item["JOBCODE"] in takeout_reg and float(item["DECTIPS"]) > 0:
                reg_cash = float(item['DECTIPS'])
                item.update({'DECTIPS': (item['DECTIPS']-reg_cash)})
                tipshare += reg_cash
            if item["SALES"] > 0:
                tltsales = tltsales + item["SALES"]
            if item["JOBCODE"] in labor_jobcode:
                if item["RATE"] > 0:
                    regpay = item["RATE"] * item["HOURS"]
                    overpay = (item["RATE"]* 1.5) * item["OVERHRS"]
                    totalpay = regpay + overpay
                    tltpay += totalpay
                    tlt_reg_hour += item["HOURS"]
                    tlt_over_hours += item["OVERHRS"]
                    item.update({"REGPAY": regpay})
                    item.update({"OVERPAY": overpay})
                    item.update({"TOTALPAY": totalpay})
            item.update({"SRVTIPS": round(server_tips,2)})
            item.update({"TIPSHR_CON": round(tipshare,2)})

        salary_pay = 0
        salary = ''
        if config.get("DEFAULT", "salary") == 'True':
            salary = ', Salary'
            salary_pay += salaried['RATE'] * salaried['HOURS']
            salary_pay += (salaried['RATE'] * 1.5) * salaried['OVERHRS']
            tltpay += (salary_pay.sum()/payroll_days)

        tip_pool = 0
        for item in working_dict:
            if float(item["TIPSHR_CON"]) > 0:
                if item["JOBCODE"] in server_jobcode:
                    server_tipshrpool += round(float(item["TIPSHR_CON"]),2)
                tip_pool += round(float(item["TIPSHR_CON"]),2)
        #print("Tip Pool: " + str(tip_pool))          

        #Calculate total hours
        total_hours = 0
        for item in working_dict:
            x = item["JOBCODE"]
            if x in tipout_recip:
                total_hours += round(float(item['HOURS']),2) + round(float(item['OVERHRS']),2)
        #print("Total Hours: " + str(total_hours))

        p_hourly_rate = 0
        hourly_rate = 0
        if tip_pool != 0:
            hourly_rate = (tip_pool / total_hours)
            p_hourly_rate = hourly_rate
        #print("Hourly Rate: " + str(hourly_rate))

        jobname = jobs.loc[(jobs['ID'] == 8),'SHORTNAME'].values[0]
        datetime_rate = datetime.datetime.strptime(day, "%Y%m%d")
        tips = pd.DataFrame(data={'Date': [datetime_rate.strftime("%a %b %e")], 'Tip Hourly': [p_hourly_rate], 'TO Cash': [reg_cash], 'Server Tipshare': [server_tipshrpool],'TO CC tips': [to_cctips], 'Total Tip Pool': [tip_pool], 'Total Tipped Hrs': [total_hours]})
        labor = pd.DataFrame(data={'Date': [datetime_rate.strftime("%a %b %e")],'Tracked Jobs': [jobname + '' + salary], 'Total Pay': [tltpay], 'Total Sales': [tltsales], 'Labor Rate (%)': [salesZero(tltsales, tltpay)], 'Regular Hrs': [tlt_reg_hour], 'Overtime Hrs': [tlt_over_hours], 'Total Hours': [tlt_over_hours + tlt_reg_hour]})
        ##OVERTIME -- Overpay specifies only the amount paid in additon to the normal rate. for example, rate is 10/hr, with 1 hour overtime at the rate of 15. the overpay shows 1 * 5, meaning $5 on top of the regular pay for the overtime hour only
        
        #Adding tipshare to working_dict
        for item in working_dict:
            portion = 0
            x = item["JOBCODE"]
            if x in tipout_recip:
                portion += ((float(item['HOURS']) + float(item["OVERHRS"])) * hourly_rate)
                item.update({"TIPOUT": portion})
            else:
                item.update({"TIPOUT": 0})

        #dataframe to csv
        working_pd = pd.DataFrame(list(working_dict))
        working_pd.to_csv('csv/'+ day +'_labordata.csv', index=False)
        tips.to_csv('csv/'+ day +'_tiprates.csv', index=False)
        labor.to_csv('csv/'+ day +'_laborrates.csv', index=False)
    print('\nnightly code finished\n')

def printtoexcel(days=[]):
    '''
    function assumes that a data grind has already been run, and adds them up to make a readable excel report
    '''
    #sum up all csvs and make it a readable report
    print('Concatenating Days')#, list(days))

    files = glob.glob('output/*.xlsx')
    for f in files:
        os.remove(f)

    df = pd.concat((pd.read_csv('csv/'+ date +'_labordata.csv') for date in days), ignore_index=True)
    tips = pd.concat((pd.read_csv('csv/'+ date +'_tiprates.csv') for date in days), ignore_index=True)
    labor = pd.concat((pd.read_csv('csv/'+ date +'_laborrates.csv') for date in days), ignore_index=True)

    df.groupby(['EMPLOYEE','SYSDATEIN'], as_index=True)
    df = df.drop(columns=['JOBCODE'])
    df = df[['EMPLOYEE', 'SYSDATEIN', 'LASTNAME', 'FIRSTNAME', 'JOB_NAME', 'HOURS', 'OVERHRS', 'SRVTIPS', 'TIPOUT', 'DECTIPS', 'CCTIPS', 'SALES', 'TIPSHR_CON', 'COUTBYEOD','INHOUR','INMINUTE','OUTHOUR','OUTMINUTE']]
    df = df.sort_values(['EMPLOYEE', 'JOB_NAME'], ascending=(True, False))

    coutbyeod = df.loc[(df['COUTBYEOD']=="Y")]
    coutxlsx = pd.ExcelWriter('output/bad clockouts_' + str(days[0]) + '_' + str(days[len(days)-1]) + '.xlsx')
    coutbyeod.to_excel(coutxlsx, sheet_name='End of day Clockouts', index=False, header=True, float_format="%.2f")

    #write totals
    tdf = df.pivot_table(df, index=['LASTNAME', 'FIRSTNAME','JOB_NAME'], aggfunc=np.sum, fill_value=np.NaN, margins=True, margins_name='TOTAL')
    tdf = tdf.drop(columns=['INHOUR', 'INMINUTE', 'OUTHOUR', 'OUTMINUTE'])
    tdf = tdf[['HOURS', 'OVERHRS', 'SRVTIPS', 'TIPOUT', 'DECTIPS']]

    #renaming a few headers, adding a meals category
    tdf = tdf.rename(columns={'OVERHRS':'OVRTIME'})
    tdf = tdf.rename(columns={'DECTIPS':'DECLTIPS'})
    tdf['MEALS'] = np.nan

    #making zeros blank
    cols = ['HOURS', 'OVRTIME', 'SRVTIPS', 'TIPOUT', 'DECLTIPS']
    tdf[cols] = tdf[cols].replace({0:np.nan})

    ttl_writer = pd.ExcelWriter('output/total_'+ str(days[0]) + '_' + str(days[len(days)-1]) + '.xlsx')
    tdf.to_excel(ttl_writer, sheet_name='Payroll_total', index=True, header=True, float_format="%.2f")

    tips['Tip Hourly'] = tips['Tip Hourly'].replace({0:np.nan})
    tips.at['Total', 'TO Cash'] = tips['TO Cash'].sum()
    tips.at['Total', 'Server Tipshare'] = tips['Server Tipshare'].sum()
    tips.at['Total', 'TO CC tips'] = tips['TO CC tips'].sum()
    tips.at['Total', 'Total Tip Pool'] = tips['Total Tip Pool'].sum()
    tips.at['Total', 'Total Tipped Hrs'] = tips['Total Tipped Hrs'].sum()
    tips.at['Average', 'Tip Hourly'] = tips['Tip Hourly'].mean(skipna=True)
    tips_writer = pd.ExcelWriter('output/tiprates_'+ str(days[0]) + '_' + str(days[len(days)-1]) + '.xlsx')
    tips.to_excel(tips_writer, sheet_name='Tip Rates', index=True, header=True, float_format="%.2f")

    paysum = labor['Total Pay'].sum()
    salesum = labor['Total Sales'].sum()
    rate = salesZero(salesum, paysum)
    labor.at['TOTAL', 'Total Pay'] = paysum
    labor.at['TOTAL', 'Total Sales'] = salesum
    labor.at['TOTAL', 'Labor Rate (%)'] = rate
    labor.at['TOTAL', 'Regular Hrs'] = labor['Regular Hrs'].sum()
    labor.at['TOTAL', 'Overtime Hrs'] = labor['Overtime Hrs'].sum()
    labor.at['TOTAL', 'Total Hours'] = labor['Total Hours'].sum()
    labor_writer = pd.ExcelWriter('output/laborrates_'+ str(days[0]) + '_' + str(days[len(days)-1]) + '.xlsx')
    labor.to_excel(labor_writer, sheet_name='Labor Rates', index=True, header=True, float_format="%.2f")

    #write indiviudal, if option is selected
    if config.get("DEFAULT", "debug") == 'True':
        ind_df = df.sort_values(by='SYSDATEIN')
        ind_writer = pd.ExcelWriter('output/nightly_' + str(days[0]) + '_' + str(days[len(days)-1]) + '.xlsx')
        ind_df.to_excel(ind_writer, sheet_name='Payroll_nightly', index=False, header=True, float_format="%.2f")

        workbook_ind = ind_writer.book
        worksheet_ind = ind_writer.sheets['Payroll_nightly']
        format1 = workbook_ind.add_format({'border': 1})
        worksheet_ind.set_column('A:R', 10, format1)

        ind_writer.save()
    else:
        pass

    #excel formatting
    header = '&CREPORT DATES: ' + (datetime.datetime.strptime(days[0], "%Y%m%d").strftime("%a %b %d, %Y")) + ' --- ' + (datetime.datetime.strptime(days[len(days)-1], "%Y%m%d").strftime("%a %b %d, %Y")) + ''
    footer = '&CDATE PRINTED: ' + qtoday.strftime("%a %b %d, %Y, %H:%M:%S")
    
    workbook_ttl = ttl_writer.book
    worksheet_ttl = ttl_writer.sheets['Payroll_total']
    format1 = workbook_ttl.add_format({'border': 1, 'font_size': 11.5})
    worksheet_ttl.set_column('A:C', 10.25, format1)
    worksheet_ttl.set_column('D:I', 8, format1)
    worksheet_ttl.set_default_row(22.5)
    worksheet_ttl.set_header(header)
    worksheet_ttl.set_footer(footer)


    workbook_coutxlsx = coutxlsx.book
    worksheet_coutxlsx = coutxlsx.sheets['End of day Clockouts']
    format1 = workbook_coutxlsx.add_format({'border': 1})
    worksheet_coutxlsx.set_column('A:R', 10, format1)
    worksheet_coutxlsx.set_header(header)
    worksheet_coutxlsx.set_footer(footer)

    tips_wrkbook = tips_writer.book
    tips_wrksheet = tips_writer.sheets['Tip Rates']
    format1 = tips_wrkbook.add_format({'border': 1, 'num_format': '_(* #,##0.00_);_(* (#,##0.00);_(* "-"??_);_(@_)'})
    tips_wrksheet.set_column('B:H', 15, format1)
    tips_wrksheet.set_header(header)
    tips_wrksheet.set_footer(footer)
    tips_wrksheet.set_landscape()

    labor_wrkbook = labor_writer.book
    labor_wrksheet = labor_writer.sheets['Labor Rates']
    format1 = labor_wrkbook.add_format({'border': 1, 'num_format': '_(* #,##0.00_);_(* (#,##0.00);_(* "-"??_);_(@_)'})
    labor_wrksheet.set_column('B:I', 13, format1)
    labor_wrksheet.set_header(header)
    labor_wrksheet.set_footer(footer)
    labor_wrksheet.set_landscape()

    coutxlsx.save()
    ttl_writer.save()
    tips_writer.save()
    labor_writer.save()

    print('\nreports created\n')

#main code
if __name__ == "__main__":
    #UX Code to collect a proper date format
    root = Tk()
    root.geometry("400x600")
    root.title("Pyroll App")

    def grab_date():
        label.config(text="First Day Selected: " + cal.get_date())
        global start_date
        global end_date
        start_date = cal.selection_get()
        end_date = cal.selection_get()
    def grab_date_two():
        label_two.config(text="Last Day Selected: " + cal.get_date())
        global end_date
        end_date = cal.selection_get()
    def yesterday():
        global start_date
        start_date = date.today() - timedelta(days=1)
        global end_date
        end_date = date.today() - timedelta(days=1)
        label.config(text="First Day Selected: " + str(start_date))
    def popup():
        label_pop = Label(root, text="\nTips will now be processed")
        label_pop.pack()
        button_pop = Button(root, text="Okay", command=root.destroy)
        button_pop.pack(pady=10)
        cal.destroy()
        button.destroy()
        button_two.destroy()
        cls_button.destroy()
    #when the settings button gets clicked
    def settings():
        popup = Tk()
        popup.geometry("400x350")
        popup.title("Settings")
        label_pop = Label(popup, text="\nAdjust settings")
        label_pop.pack()
        #tipshare variable
        tipshrlbl = Label(popup, text='Enter tipshare percent as decimal (ex. 0.03 for 3%)')
        tipshrlbl.pack(pady=5)
        tipshr = Entry(popup)
        tipshr.pack()
        tipcfg = tipshr.get()
        tipshr_btn = Button(popup, text='Set Tipshare percent', command=config.set("DEFAULT", "tip share percent", tipcfg))
        config.write(open('config.ini','w'))
        tipshr_btn.pack()
        #database location 
        dtbselbl = Label(popup, text='Select the location of the "data" folder in Aloha')
        dtbselbl.pack(pady=5)
        dtbse = Entry(popup)
        dtbse.pack()
        dtbsecfg = tipshr.get()
        dtbse_btn = Button(popup, text='Set Database location', command=config.set("DEFAULT", "databaseloc", dtbsecfg))
        config.write(open('config.ini','w'))
        dtbse_btn.pack()
    def on_closing():
        root.destroy()
        sys.exit()

    start_date = ''
    end_date = ''    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    month = int(date.today().strftime("%m"))
    year = int(date.today().strftime("%Y"))
    main_label = Label(root, 
        text="Must be processed after the end of last day for payroll\n \nSelecting today (" + qtoday.strftime("%m-%d-%Y") + ") or future days will cancel process\n \nIf changes were made in POS, tips must be run again")
    main_label.pack(pady=5)
    tipshr_percent = str(float(config.get("DEFAULT", "tip share percent"))*100)
    label_tip = Label(root, text="Tip share percent: "+ tipshr_percent + "%\n")
    label_tip.pack(pady=5)
    cal = Calendar(root, selectmode="day", firstweekday="sunday", showweeknumbers=False, 
        showothermonthdays=False, year=year, month=month, date_pattern="mm-dd-yyyy")
    cal.pack(pady=20)
    #settings = Button(root, text="Settings", command=settings)
    #settings.pack(pady=5)
    yest = Button(root, text="Yesterday", command=yesterday)
    yest.pack(pady=10)
    button = Button(root, text="Select First Day", command=grab_date)
    button.pack(pady=10)
    button_two = Button(root, text="Select Last Day", command=grab_date_two)
    button_two.pack(pady=10)
    cls_button = Button(root, text="PROCESS TIPS", command=popup)
    cls_button.pack(pady=15)
    label = Label(root, text="")
    label.pack(pady=5)
    label_two = Label(root, text="")
    label_two.pack(pady=5)

    root.mainloop()

    startday = start_date #save into different value, so it can be used to write file names
    delta = datetime.timedelta(days=1)
    dayofreport = ''
    global days
    days = []

    #process loop
    while start_date <= end_date:
        dayofreport = start_date.strftime("%Y%m%d")
        print("now processing " + dayofreport + "\n")
        processdatabase(dayofreport)
        processtips(dayofreport)
        days.append(dayofreport)
        start_date += delta

    printtoexcel(days)

    #files cleanup
    if config.get("DEFAULT", "debug") == 'True':
        pass
    else:
        files = glob.glob('csv/*.csv')
        #file_2 = glob.glob('output/*.xlsx')
        for f in files:
            os.remove(f)

    print('process complete -- exiting\n')