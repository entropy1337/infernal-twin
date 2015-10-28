This tool is created to aid the penetration testers in assessing wireless security. 
Author is not responsible for misuse. Please read instructions thoroughly.  

Usage: python InfernalWireless.py (from the same folder where you codes exist)

For any comments and suggestions please email on 3ntr0py1337@gmail.com

**NOTE:** Please make sure to run the 'configure under File menu to install required software'

FAQ:

1. I have a problem with connecting to Database

Solution: 

There seem to be few issues with Database connectivity. The solution is to create a new user on the database and use that user for launching the tool. Follow the following steps. 

1. Delete dbconnect.conf file from the Infernalwireless folder

2. Run the following command from your mysql console.

mysql>`use mysql;`

mysql>`CREATE USER 'root2'@'localhost' IDENTIFIED BY 'enter the new password here';`

mysql>`GRANT ALL PRIVILEGES ON \*.\* TO 'root2'@'localhost' WITH GRANT OPTION;`

3. Try to run the tool again. 

   Thanks to `@lightos` for mentioning fix. 


## Release Notes: 

### NEW FEATURES:

* GUI Wireless security assessment SUIT

* Impelemented 

* WPA2 hacking

* WEP Hacking

* WPA2 Enterprise hacking

* Wireless Social Engineering

* SSL Strip

* Report generation 

* PDF Report

* HTML Report

* Note taking function

* Data is saved into Database

* Network mapping 

* MiTM 

* Probe Request


### CHANGES:

* Improved compatibility 

* Report improvement

* Better NAT Rules


### BUG FIXES:

* Wireless Evil Access Point traffic redirect
* Fixed WPA2 Cracking
* Fixed Infernal Wireless
* Fixed Free AP
* Check for requirements
* DB implementation via config file
* Improved Catch and error
* Check for requirements
* Works with Kali 2

### Coming Soon: 

* Parsing t-shark log files for gathering creds and more

* More attacks.

### BUGS exptected: 

* Wireless card might not be supported

* Windodw might crash 

* Freeze

* A lot of work to be done, but this tool is still being developed. 

Thanks and Credits: 

* Special thanks to all my friends for comments

* creators: 

..* Aircrack

..* SSL Strip

..* Online Community

..* others whom I forgot to mention. 



