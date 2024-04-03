from datetime import datetime, timedelta
import sqlite3
from tkinter import StringVar, Tk, Label, Frame
from tkinter import ttk
from tkinter.messagebox import showinfo
from tkinter.ttk import Button, Combobox, Frame
from report_writer import ReportWriter

class AdjustmentsGui():

    def __init__(self, icon="", title="Title"):
        self.adjust_window = Tk()
        self.adjust_window.geometry("400x600")
        self.adjust_window.iconbitmap(icon)
        self.adjust_window.wm_title(title)
        self.adjust_frame = Frame(self.adjust_window)
        self.adjust_frame.grid()
        self.today = datetime.today()
        self.day = 19700101

        #initalizers 
        self.Employee=0
        self.Job_Name=''
        self.Adjustment=0
        self.Date=19700101
        self.AdjustedBy=''
        self.AdjustedOn=19700101
        def set_day(e):
            self.day = self.date_dropdown.get()
            self.run_date()
        #startgui
        dl = Label(self.adjust_frame, text="Choose a Date")
        dl.grid(row=2,column=2)
        # Create a list of dates from the previous 15th or end of month date, to today
        date_list = [self.today - timedelta(days=x) for x in range(20)]
        date_list = [x.strftime("%a, %b %d, %y") for x in date_list]
        label2 = Label(self.adjust_frame, text="**adjustments must be entered before\nexporting to payroll**")
        label2.config(font=("Courier", 10))
        label2.grid(row=3,column=2)
        self.date_dropdown = Combobox(self.adjust_frame, values=date_list)
        self.date_dropdown.grid(row=4  ,column=2)
        self.date_dropdown.bind("<<ComboboxSelected>>", set_day)

    def add_adjustment_to_db(self, _Employee, _Job_Name, _Adjustment, _Date, _AdjustedBy, _AdjustedOn):
        '''takes in adjustments and adds them to the database'''
        conn = sqlite3.connect('data/adjustments.db')
        data = (_Employee, _Job_Name, _Adjustment, _Date, _AdjustedBy, _AdjustedOn)
        #data = (1001, 'FRYCOOK', -5, '20240323','ALEX','20240401')
        sql = '''INSERT INTO tip_adjustments (EMPLOYEE, JOB_NAME, ADJUSTMENT, DATE, ADJUSTEDBY, ADJUSTEDON)
                VALUES (?, ?, ?, ?, ?,?)'''
        conn.execute(sql, data)
        conn.commit()
        conn.close()
        showinfo('Note',"Adjustment saved")

    def run_date(self):
        self.day = datetime.strptime(self.day, "%a, %b %d, %y").strftime('%Y%m%d')
        result = ReportWriter(self.day, self.day).print_to_json(
            'labor_main', json_fmt=True)
        if type(result) == 'empty':
            showinfo('Note', "There is no data to display for this selection\n(This is not an error)")
            return '' #exit the program if no data to display
        result = result[result['TTL_CONTRIBUTION'] > 0]
        result.drop(result.tail(1).index,inplace=True)
        fn = (result['FIRSTNAME'] + ' | ' + result['JOB_NAME']).to_list()
        psl1 = Label(self.adjust_frame, text="Primary Server")
        psl1.grid(row=7,column=2)
        dropdown_val = StringVar(self.adjust_frame)
        primary_selection_dropdown = Combobox(self.adjust_frame, values=fn)
        primary_selection_dropdown.grid(row=8,column=2)

        psl2 = Label(self.adjust_frame, text="Enter adjustment\nNegative values allowed (deductions)")
        psl2.grid(row=9,column=2)
        adjustment_amt_selector = ttk.Spinbox(self.adjust_frame,increment=1)
        adjustment_amt_selector.grid(row=10,column=2)
        psl3 = Label(self.adjust_frame, text="Enter your name\n(who is entering this adjustment)")
        psl3.grid(row=11,column=2)
        who_adjusted_input = ttk.Entry(self.adjust_frame)
        who_adjusted_input.grid(row=12,column=2)
        save_button = Button(self.adjust_frame, text="submit_adjustment", command=self.add_adjustment_to_db(self.Employee, self.Job_Name, self.Adjustment, self.Date, self.AdjustedBy, self.AdjustedOn))
        save_button.grid(row=13,column=2)

    def mainloop(self):
        self.adjust_window.mainloop()

if __name__ == "__main__":
    AdjustmentsGui().mainloop()