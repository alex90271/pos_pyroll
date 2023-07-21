
### --- NOTES

### --- INSTALL INSTRUCTIONS

    1. Run `python -m pip install -r "requirements.txt"`

### ---FRONTEND:

    Using tkinter

    Requires you install https://wkhtmltopdf.org/

    Download binaries, and unzip the wkhtmltox to the source directory

### ---BACKEND:

    Pyinstaller Compile Command: 
        pyinstaller server.py --onefile --add-data "templates;templates" --add-data "wkhtmltox;wkhtmltox" 