Steam Engines
The automated way to find out the current market share of game engines on Steam!

YOU NEED
--------
Python 3
pip install wptools (Install pip if you don't have it, or find another way to install wptools.)

HOW TO USE
----------
1. Run GetSteamApps.py (1-2 seconds)

1.2. Export file name
Enter a file name here, like steamapps.txt

2. Run SteamEngines.py

2.1. Input Steam file name
Enter the file name you entered, like steamapps.txt

2.2. How many do you want to research?
Enter how many Steam apps you want to research.
The more you research, the more accurate the data will be,
but the longer it will take. The script uses the earliest
Steam Apps, i.e. it filters out the newest apps if you choose
a number less than maximum.
If 0 is entered, it will research all apps.

2.3. How many threads do you want to use?
The more threads, the faster it will go. HOWEVER:
It will consume more CPU, more RAM, and more network.
Also, don't put too many threads! Put too many, and
Wikipedia admins may ban you for abusing resources.
10 threads is what I used, it should be enough.
(4 hours for all Steam apps)

2.4. CLOSE ENGINES.CSV if you have it open!

2.5. Wait. This step might take several hours or even days.
For reference, 10 threads on 60,000 games is 4 hours.

2.6. Once you're done, open engines.csv in Excel or another spreadsheet program.

This is under the MIT license.
Contact me: limdingwen@gmail.com, or /r/limdingwen on Reddit.