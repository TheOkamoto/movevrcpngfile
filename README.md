This simple Python script moves PNG files from one folder to another.

Accepted command line parameters:

    --delay       The delay before moving files in seconds.
    
    --source      The source folder.
    
    --destination The destination folder.
    
You can also freely edit the `config.ini` file to change parameters manually.

![image](https://github.com/TheOkamoto/movevrcpngfile/assets/42682615/dade63b5-6d06-479c-b32e-5e2a8161c6f5)

Tested with Python 3.11.5 and 3.12

To run the script you will need to install the `watchdog` and `rich` packages via `pip`

You can do it by writing the following commands:

`pip install rich`

`pip install watchdog`

To run the application you can use the following command from Powershell or cmd:

`python .\vrcpicturetransfer.py`

You can also compile into a single Windows `.exe` executable by first installing pyinstall

`pip install pyinstall`

And finally, you can use this command to compile into an executable:

`pyinstaller --onefile .\vrcpicturetransfer.py`
