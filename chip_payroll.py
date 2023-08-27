import tkinter as tk
from tkinter import ttk
from gui import MainGui

if __name__ == "__main__":
    # Create a window
    window = tk.Tk()
    window.geometry("300x400")
    icon = "assets\pyroll_ico.ico"
    title = "Payroll and Tipshare report tool"
    window.iconbitmap(icon)
    window.wm_title(title)
    
    please_wait_message = tk.Label(window, text="Loading.. This will take a moment", font=("Arial", 10))
    please_wait_message.pack(padx=5)
    pb = ttk.Progressbar(
        window,
        orient='horizontal',
        mode='indeterminate',
        length=160
    )
    pb.pack(padx=5)
    pb.start()

    #launch the main GUI
    gui = MainGui(icon=icon, title=title)
    gui.main_window()
    gui.kill_launch_window(window)

    window.mainloop()

