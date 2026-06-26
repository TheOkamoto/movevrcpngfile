This simple Python script moves PNG files from one folder to another.

Accepted command line parameters:

    --delay       The delay before moving files in seconds.
    
    --source      The source folder.
    
    --destination The destination folder.
    
You can also freely edit the `config.ini` file to change parameters manually.

![image](https://github.com/TheOkamoto/movevrcpngfile/assets/42682615/dade63b5-6d06-479c-b32e-5e2a8161c6f5)

Tested with Python 3.11, 3.12, and 3.13.

### Installation

To run the script, you will need to install the required dependencies via `pip`. 
We made it easy by including a `requirements.txt` file. You can install everything at once by running the following command:

`pip install -r requirements.txt`

### Usage

To run the application, use the following command from PowerShell or CMD:

`python .\vrcpicturetransfer.py`

### Compiling to an Executable (.exe)

You can also compile the script into a single Windows `.exe` executable. First, install PyInstaller:

`pip install pyinstaller`

Then, use this command to compile it into an executable:

`pyinstaller --onefile .\vrcpicturetransfer.py`