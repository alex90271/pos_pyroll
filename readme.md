
### --- NOTES

### --- INSTALL INSTRUCTIONS

    1. Run `python -m pip install -r "requirements.txt"`

### --- FRONTEND:

    Using tkinter

    Requires you install https://wkhtmltopdf.org/

    Download binaries, and unzip the wkhtmltox to the source directory

### --- BACKEND:

    Pyinstaller Compile Command: 
        pyinstaller chip_payroll.py --noconsole --hidden-import babel.numbers --add-data "templates/*;templates" --add-data "wkhtmltox/bin/*;wkhtmltox/bin" --add-data "wkhtmltox/include/*;wkhtmltox/include" --add-data "assets/*;assets"

    NOTE: If using --onefile arg, templates, wkhtmltox, and assets must be added separately
        pyinstaller chip_payroll.py --onefile --noconsole --hidden-import babel.numbers --icon=assets\pyroll_ico.ico