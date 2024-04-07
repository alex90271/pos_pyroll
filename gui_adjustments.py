from datetime import datetime, timedelta
import sqlite3
from tkinter import StringVar, Tk, Label, Frame
from tkinter import ttk
from tkinter.messagebox import showinfo
from tkinter.ttk import Button, Combobox, Frame
from report_writer import ReportWriter
from process_labor import ProcessLabor as labor


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
        self.adjustment_amt_selector = ttk.Spinbox()
        self.primary_selection_dropdown = Combobox()
        self.who_adjusted_input = ttk.Entry()


        #initalizers 
        self.Employee=0
        self.Job=0
        self.Adjustment=0
        self.Date=19700101
        self.AdjustedBy=''
        self.AdjustedOn=19700101
        def set_day(e):
            self.day = self.date_dropdown.get()
            self.Date = datetime.strptime(self.day, "%a, %b %d, %y").strftime('%Y%m%d')
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

    def set_adjustedby(self):
        self.AdjustedBy = self.who_adjusted_input.get()
        self.AdjustedOn = datetime.today().strftime('%Y%m%d')

    def set_adjustment(self):
        self.Adjustment = self.adjustment_amt_selector.get()
        self.Adjustment = float(self.Adjustment)

    def set_employee_job_date(self):
        emp,job = self.primary_selection_dropdown.get().split(', ')
        self.Employee = int(emp)
        self.Job = int(job)

    def add_adjustment_to_db(self):
        '''takes in adjustments and adds them to the database'''
        self.set_adjustedby()
        self.set_adjustment()
        self.set_employee_job_date()
        #date is set earlier on, which is needed to run the employee list
        print(self.Date)

        if self.AdjustedOn == 19700101:
            showinfo('Note',"Something went wrong")
        else:
            conn = sqlite3.connect('data/adjustments.db')
            data = (self.Employee, self.Job, self.Adjustment, self.Date, self.AdjustedBy, self.AdjustedOn)
            #data = (1001, 8, -5, '20240323','ALEX','20240401')
            sql = '''INSERT INTO tip_adjustments (EMPLOYEE, JOB, ADJUSTMENT, DATE, ADJUSTEDBY, ADJUSTEDON)
                    VALUES (?, ?, ?, ?, ?,?)'''
            conn.execute(sql, data)
            conn.commit()
            conn.close()
            showinfo('Note',"Adjustment saved")

    def run_date(self):
        self.day = datetime.strptime(self.day, "%a, %b %d, %y").strftime('%Y%m%d')
        #result = ReportWriter(self.day, self.day)
        ids = labor(self.day).get_pool_data()
        #if type(result) == 'empty':
        #    showinfo('Note', "There is no data to display for this selection\n(This is not an error)")
        #    return '' #exit the program if no data to display
        #result = result[result['TTL_CONTRIBUTION'] > 0]
        #result.drop(result.tail(1).index,inplace=True)
        ids['EMPLOYEE'] = ids['EMPLOYEE'].astype(int)
        #print(result)
        fn = (ids['EMPLOYEE'].astype(str) + ', ' + ids['JOBCODE'].astype(str)).to_list()
        psl1 = Label(self.adjust_frame, text="Primary Server")
        psl1.grid(row=7,column=2)
        self.primary_selection_dropdown = Combobox(self.adjust_frame, values=fn)
        self.primary_selection_dropdown.grid(row=8,column=2)

        psl2 = Label(self.adjust_frame, text="Enter adjustment")
        psl2.grid(row=9,column=2)
        psl2_helper = Label(self.adjust_frame, text="Negative values allowed (deductions)")
        psl2_helper.config(font=("Courier", 10))
        psl2_helper.grid(row=10,column=2)
        self.adjustment_amt_selector = ttk.Spinbox(self.adjust_frame,increment=1,from_=-500,to=500)
        self.adjustment_amt_selector.grid(row=11,column=2)

        psl3 = Label(self.adjust_frame, text="Enter your name")
        psl3.grid(row=12,column=2)
        psl3_helper = Label(self.adjust_frame, text="who is entering this adjustment")
        psl3_helper.config(font=("Courier", 10))
        psl3_helper.grid(row=13,column=2)
        self.who_adjusted_input = ttk.Entry(self.adjust_frame)
        self.who_adjusted_input.grid(row=14,column=2)

        save_button = Button(self.adjust_frame, text="submit_adjustment", command=self.add_adjustment_to_db)
        save_button.grid(row=15,column=2)

    def mainloop(self):
        self.adjust_window.mainloop()

if __name__ == "__main__":
    AdjustmentsGui().mainloop()