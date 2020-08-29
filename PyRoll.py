#required installs 
# python -m pip install tkcalendar
# python -m pip install pandas
# python -m pip install dbfread

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
from datetime import date, time
from tkinter import *
from tkcalendar import *
from dbfread import DBF

#config stuff
config = configparser.ConfigParser()
def generateconfig ():
    config['DEFAULT'] = {'tip share percent': 0.03, 'databaseloc': 'D:\\Bootdrv\\Aloha\\', 'server jobcode number': '1',
                        'take out reg job code number': '11', 'jobcode numbers to receive tips': '2,3,5,10,11,12,13,14',
                        'debug': False}
    with open ('config.ini', 'w') as configfile:
        config.write(configfile)

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
qtoday = date.today()
manual_adj = 0
working_dict = []
output_dict = []
start_date = ''
end_date = ''

#convert dbf to csv
def processdatabase (dayofreport):

    #tips, labor, etc
    labor = DBF(databaseloc + dayofreport + '/ADJTIME.Dbf')
    with open('csv/'+ dayofreport +'_labor.csv','w', newline='') as lbrexport:
        writer = csv.writer(lbrexport, delimiter=',')
        writer.writerow(labor.field_names)
        for row in labor:
            writer.writerow(list(row.values())) 
            
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
    
    #house accounts
    house = DBF(databaseloc + dayofreport + '/HSE.DBF')
    with open('csv/'+ dayofreport +'_house.csv','w', newline='') as houseexport:
        writer = csv.writer(houseexport, delimiter=',')
        writer.writerow(house.field_names)
        for row in house:
            writer.writerow(list(row.values()))

    #https://pandas.pydata.org/docs/user_guide/io.html#io-read-csv-table

    #collects sales, tips, and hours data from aloha. Data does not include jobcode names or employee names, jobcode.csv and employee.csv contain this information
    laborpd = pd.read_csv('csv/'+ dayofreport +'_labor.csv', usecols=['SYSDATEIN','INVALID','JOBCODE','EMPLOYEE','HOURS','OVERHRS','CCTIPS','DECTIPS','COUTBYEOD','SALES','INHOUR','INMINUTE','OUTHOUR','OUTMINUTE'])
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

#calculate tips
def processtips (day):
    file_name = 'csv/'+ day +'_labordata.csv'
    #don't calculate tips if COUT by EOD
    coutbyeod = pd.read_csv(file_name, usecols=['SYSDATEIN','EMPLOYEE','LASTNAME','FIRSTNAME', 'COUTBYEOD',])
    coutbyeod.loc[(coutbyeod['COUTBYEOD']=="N")]

    #config options
    takeout_reg = str(config.get("DEFAULT", "take out reg job code number")).split(',')
    server_jobcode = str(config.get("DEFAULT", "server jobcode number")).split(',')  #reg cc tips, but wanted to leave it flexible.
    tipout_recip = str(config.get("DEFAULT", "jobcode numbers to receive tips")).split(',')
    tipshare_percent = float(config.get("DEFAULT", "tip share percent"))
    #combine_tipshr = bool(config.get("DEFAULT", "combine tipshare and takeout"))

    print('\ntakeout tip contributors',takeout_reg,'\nserver jobcode',server_jobcode,'\ntipshare recipients',tipout_recip,'\ntipshare percent',tipshare_percent,'\n')

    output_dict = []
    ppl_currently_in_output_dict = []
    hourly_dict= []
    iterative_keys = ['HOURS', 'OVERHRS', 'CCTIPS', 'DECTIPS', 'SALES', 'SRVTIPS', 'TIPOUT']

    #jobcodes - 1:Server, 2:Assist/Bus, 5:Bar/Dessert, 6:Shag, 7:Dish, 8:Fry Cook, 9:Kitchen, 11:Register, 13:Pay/Phones, 14:Bagger, 50:Manager

    #process labordata into a dict object, and turn iterative keys above into floats vs strings
    with open(file_name) as labordata:
        labordata = csv.DictReader(labordata)
        working_dict = []
        for item in labordata:
            working_dict.append(item)
            for item in working_dict:
                for key in item:
                    if key in iterative_keys:
                        item[key] = float(item[key])
        
        #Calculates tips and tipouts
        for item in working_dict:
            server_tips = 0
            tipshare = 0
            hrs = 0
            if float(item["OVERHRS"]) > 0:
                hrs = float(item["HOURS"]) - float(item["OVERHRS"])
                item.update({"HOURS": hrs})
            if item["JOBCODE"] in server_jobcode:
                tipshare = float(item['SALES']) * tipshare_percent
                server_tips = float(item['CCTIPS']) - tipshare
                server_tips = server_tips
            if item["JOBCODE"] in takeout_reg:
                reg_cash = float(item['DECTIPS'])
                tipshare = float(item['CCTIPS']) + reg_cash
                item.update({'DECTIPS': (item['DECTIPS']-reg_cash)})
            item.update({"SRVTIPS": round(server_tips,2)})
            item.update({"TIPSHR_CON": round(tipshare,2)})

        tip_pool = 0
        for item in working_dict:
            if float(item["TIPSHR_CON"]) > 0:
                tip_pool += round(float(item["TIPSHR_CON"]),2)
        print("Tip Pool: " + str(tip_pool))          

        #Calculate total hours
        total_hours = 0
        for item in working_dict:
            x = item["JOBCODE"]
            if x in tipout_recip:
                total_hours += round(float(item['HOURS']),2)
        print("Total Hours: " + str(total_hours))

        p_hourly_rate = 0
        hourly_rate = 0
        if tip_pool != 0:
            hourly_rate = (tip_pool / total_hours)
            p_hourly_rate = round(hourly_rate,2)
        print("Hourly Rate: " + str(p_hourly_rate))

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
        working_pd.to_csv('csv/'+ day +'_labordata.csv')
    print('\ntips code ran fine\n')

def printtoexcel(days=[]):
    #sum up all csvs and make it a readable report
    print('Days to print', list(days))

    df = pd.concat((pd.read_csv('csv/'+ date +'_labordata.csv') for date in days), ignore_index=True)
    df.groupby(['EMPLOYEE','SYSDATEIN'], as_index=True)
    df = df.drop(columns=['Unnamed: 0', 'Unnamed: 1', 'JOBCODE'])
    df = df[['EMPLOYEE', 'SYSDATEIN', 'LASTNAME', 'FIRSTNAME', 'JOB_NAME', 'HOURS', 'OVERHRS', 'SRVTIPS', 'TIPOUT', 'DECTIPS', 'CCTIPS', 'SALES', 'TIPSHR_CON', 'COUTBYEOD','INHOUR','INMINUTE','OUTHOUR','OUTMINUTE']]
    df = df.sort_values(['EMPLOYEE', 'JOB_NAME'], ascending=(True, False))
    df = df.append(df.sum(numeric_only=True), ignore_index=True)

    coutbyeod = df.loc[(df['COUTBYEOD']=="Y")]
    coutxlsx = pd.ExcelWriter('output/bad clockouts_' + str(days[0]) + '_' + str(days[len(days)-1]) + '.xlsx')
    coutbyeod.to_excel(coutxlsx, sheet_name='End of day Clockouts', index=False, header=True, float_format="%.2f")

    #write totals
    tdf = df.pivot_table(df, index=['LASTNAME', 'FIRSTNAME','JOB_NAME'], aggfunc=np.sum)
    tdf = tdf.drop(columns=['INHOUR', 'INMINUTE', 'OUTHOUR', 'OUTMINUTE'])
    tdf = tdf[['HOURS', 'OVERHRS', 'SRVTIPS', 'TIPOUT', 'DECTIPS']]
    tdf.at['Total', 'HOURS'] = tdf['HOURS'].sum()
    tdf.at['Total', 'OVERHRS'] = tdf['OVERHRS'].sum()
    tdf.at['Total', 'SRVTIPS'] = tdf['SRVTIPS'].sum()
    tdf.at['Total', 'TIPOUT'] = tdf['TIPOUT'].sum()

    #renaming a few headers, adding a meals category
    tdf = tdf.rename(columns={'OVERHRS':'OVRTIME'})
    tdf = tdf.rename(columns={'DECTIPS':'DECLTIPS'})
    tdf['MEALS'] = np.nan

    ttl_writer = pd.ExcelWriter('output/total_'+ str(days[0]) + '_' + str(days[len(days)-1]) + '.xlsx')
    tdf.to_excel(ttl_writer, sheet_name='Payroll_total', index=True, header=True, float_format="%.2f")

    #write indiviudal
    ind_writer = pd.ExcelWriter('output/nightly_' + str(days[0]) + '_' + str(days[len(days)-1]) + '.xlsx')
    df.to_excel(ind_writer, sheet_name='Payroll_nightly', index=False, header=True, float_format="%.2f")


    #excel formatting
    workbook_ttl = ttl_writer.book
    worksheet_ttl = ttl_writer.sheets['Payroll_total']
    format1 = workbook_ttl.add_format({'border': 1, 'font_size': 11.5})
    worksheet_ttl.set_column('A:C', 10.5, format1)
    worksheet_ttl.set_column('D:I', 9, format1)
    worksheet_ttl.set_default_row(22.5)

    workbook_coutxlsx = coutxlsx.book
    worksheet_coutxlsx = coutxlsx.sheets['End of day Clockouts']
    format1 = workbook_coutxlsx.add_format({'border': 1})
    worksheet_coutxlsx.set_column('A:R', 10, format1)

    workbook_ind = ind_writer.book
    worksheet_ind = ind_writer.sheets['Payroll_nightly']
    format1 = workbook_ind.add_format({'border': 1})
    worksheet_ind.set_column('A:R', 10, format1)

    coutxlsx.save()
    ind_writer.save()
    ttl_writer.save()
    print('\noutput created\n')

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
        
    root.protocol("WM_DELETE_WINDOW", on_closing)
    month = int(date.today().strftime("%m"))
    main_label = Label(root, 
        text="Must be processed after the end of last day for payroll\n \nSelecting today (" + qtoday.strftime("%m-%d-%Y") + ") or future days will cancel process\n \nIf changes were made in POS, tips must be run again")
    main_label.pack(pady=5)
    tipshr_percent = str(float(config.get("DEFAULT", "tip share percent"))*100)
    label_tip = Label(root, text="Tip share percent: "+ tipshr_percent + "%\n")
    label_tip.pack(pady=5)
    cal = Calendar(root, selectmode="day", firstweekday="sunday", showweeknumbers=False, 
        showothermonthdays=False, year=2020, month=month, date_pattern="mm-dd-yyyy")
    cal.pack(pady=20)
    #settings = Button(root, text="Settings", command=settings)
    #settings.pack(pady=5)
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
    days =[]

    #process loop
    while start_date <= end_date:
        print("now processing " + dayofreport + "\n")
        dayofreport = start_date.strftime("%Y%m%d")
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
        for f in files:
            os.remove(f)

    print('process complete -- exiting\n')