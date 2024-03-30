Time Clock

Simple time clock for tracking employees hours. 


Requirements
- Python 3.12 or higher
- nssm to run as a service on windows

Setup on windows
- setup.bat creates the python enviroment and downloads the required packages
- nssm install - adds as a service on windows, just point the service to timeclock.bat 

Backups
- all data stored in timeclock.db