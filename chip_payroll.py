import tkinter as tk
from gui import MainGui

if __name__ == "__main__":
    # Create a window
    window = tk.Tk()
    window.geometry("300x400")
    icon = "assets\pyroll_ico.ico"
    title = "Payroll and Tipshare report tool"
    window.iconbitmap(icon)
    window.wm_title(title)
    # Create an animated loading symbol
    loading_symbol = tk.Label(image=tk.PhotoImage(file="assets\cog.gif"))
    loading_symbol.pack()

    # Create a "please wait" message
    please_wait_message = tk.Label(text="Loading.. This will take a moment", font=("Arial", 10))
    please_wait_message.pack()

    #after 5 seconds, close the window
    window.after(5000, window.destroy)

    #launch the main GUI
    MainGui(icon=icon, title=title).launch()

    window.mainloop()