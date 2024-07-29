
### --- NOTES

### --- INSTALL INSTRUCTIONS

    Note: This script was designed to run on Windows 10 or 11 only. 

    1. Create your environment `python -m venv .venv`\
        a. Activate the script on the windows system, using an elevated powershell terminal `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned`
        b. Connect to the environment (windows) `./.venv/Scripts/Activate.ps1`

    2. Install dependencies with `python -m pip install -r "requirements.txt"`

    3. Download WKHTML to PDF here: https://wkhtmltopdf.org/ 
        a. Select 7z Archive (ensure you have software to extract the archive)
        b. Move the extracted wkhtmltox file into the root directory

    4. Run `python chip_payroll.py` to launch
        a. After first launch you will need to configure settings[v3].json to point to your database(or set debug to true)

### --- BUILDING EXECUTABLE:

    Pyinstaller Compile Command: 
        `pyinstaller chip_payroll.py --noconsole --hidden-import babel.numbers --add-data "templates/*;templates" --add-data "wkhtmltox/bin/*;wkhtmltox/bin" --add-data "wkhtmltox/include/*;wkhtmltox/include" --add-data "assets/*;assets`

    To use the custom icon you can add the argument `--icon=assets\pyroll_ico.ico"`

    If using --onefile arg, templates, wkhtmltox, and assets must be added separately
        `pyinstaller chip_payroll.py --onefile --noconsole --hidden-import babel.numbers`