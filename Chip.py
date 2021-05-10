# python -m pip install tkcalendar
# python -m pip install pandas
# python -m pip install dbfread
# python -m pip install xlsxwriter
# python -m pip install python-quickbooks

import timeit
import numpy as np
import sys
import os
import babel.numbers
import zerorpc
import gevent, signal
from gen_rpt import gen_rpt
from datetime import timedelta, date, datetime
from tkcalendar import Calendar
from tkinter import Tk, Label, Button
from cfg import cfg

class rpt_out():
    def __init__(self):
        self.root = Tk()
        self.root.geometry("400x600")
        self.root.title("Pyroll App")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.cal = Calendar(self.root, selectmode="day", firstweekday="sunday", showweeknumbers=False, 
            showothermonthdays=False, year=int(date.today().strftime("%Y")), month=int(date.today().strftime("%m")), date_pattern="mm-dd-yyyy")

    def grab_date(self):
        label = Label(self.root, text="")
        label.config(text="First Day Selected: " + self.cal.get_date())
        global day_one
        day_one = self.cal.selection_get().strftime("%Y%m%d")
        label.pack(pady=5)

    def grab_date_two(self):
        label_two = Label(self.root, text="")
        label_two.config(text="Last Day Selected: " + self.cal.get_date())
        global day_two
        day_two = self.cal.selection_get().strftime("%Y%m%d")
        label_two.pack(pady=5)

    def on_closing(self):
        self.root.destroy()
        sys.exit()

    def launch(self):
        main_label = Label(self.root, 
            text="""Must be processed after the end of last day for payroll\n 
                \nSelecting today (""" + date.today().strftime("%m-%d-%Y") + """) or future days will cancel process\n
                \nIf changes were made in POS, tips must be run again""")
        main_label.pack(pady=5)
        self.cal.pack(pady=20)
        def popup():
            label_pop = Label(self.root, text="\nTips will now be processed")
            label_pop.pack()
            button_pop = Button(self.root, text="Okay", command=self.root.destroy)
            button_pop.pack(pady=10)
            self.cal.destroy()
            button.destroy()
            button_two.destroy()
            cls_button.destroy()
        button = Button(self.root, text="Select First Day", command=self.grab_date)
        button.pack(pady=10)
        button_two = Button(self.root, text="Select Last Day", command=self.grab_date_two)
        button_two.pack(pady=10)
        cls_button = Button(self.root, text="PROCESS TIPS", command=popup)
        cls_button.pack(pady=15)

        self.root.mainloop()

class chipAPI(gen_rpt):

    def echo(self, text):
        return text

    def print(self, rpt):
        #TODO implement hook to gen_rprt
        pass
    
    def set_json(self, json_name):
        os.environ['json_name'] = json_name
        return json_name

if __name__ == '__main__':
    print("\nloading chip.py\n")

    def electron_hook():
        port = 1234
        addr = 'tcp://127.0.0.1:' + port
        s = zerorpc.Server(chipAPI())
        s.bind(addr)
        gevent.signal(signal.SIGTERM, s.stop)
        gevent.signal(signal.SIGINT, s.stop)  # ^C

        s.run()

    def main():
        #you can clear the enviroment and set the json_name to read a different settings file, or simply generate a new one with a different name
        #if no variable is set here, it will use the default, set in cfg.py 'chip.json'
        #os.environ.clear()
        #os.environ['json_name'] = 'chip.json' #str(sys.argv[1])
        #day_one = str(sys.argv[2]) #'20210101'
        #day_two = str(sys.argv[3]) #'20210115'

        #full command: python chip.py json_name day_one day_two
        #testing: python chip.py chip.json 20210101 20210115
        print('Args: ' + str(sys.argv) + '\n')
        print('Loading from: ' + cfg().query('SETTINGS','database'))

        rpt_out().launch() #--- legacy UX
        electron_hook()

        #if a second day is not selected, make the date range the same days
        [gen_rpt(day_one).print_to_excel(rpt) for rpt in list(['tip_rate', 'labor_main', 'labor_rate', 'cout_eod', 'labor_total'])]

    r = 1
    f = timeit.repeat("main()", "from __main__ import main", number=1, repeat=r)
    print("completed with an average of " + str(np.round(np.mean(f),2)) + " seconds over " + str(r) + " tries \ntotal time: " + str(np.round(np.sum(f),2)) + "s")


