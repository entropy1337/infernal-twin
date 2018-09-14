## Infernal-Wireless v2.6
Release 2.3

- Improved and Compatibility on Kali Linux 2018
- Added Visual Representation of Wireless Scan 
- Added Visual Representation of Probe Requests and Map per SSID requested by Devices
- Updated MAC address mapping
- Added MAC address mappting on probe request devices
- Evil Twin Attack on WPA2 PSK (with provided credentials)
- Development Testing of Automated Wireless Scan Wizard
- MiTM improvement and integration with Metasploit
- Improved Social Engineering Aspects over Wireless Network 
- Added Beacon signal on wireless scan results
- Organized File Structure and Layout of the tool
- Created dedicated Folder for Logs and management 


## Infernal-Wireless v2.6

Release 2.6.11

## Features added and improved: 

- Menu to retrieve logs are added 


## Infernal-Wireless v2.6

Release 2.6.10

## Features added and improved: 

- Added BeeF XSS framework Integration 
- Added HTTP Traffic View within tool
- Improved Infenral Wireless Attack
- Visual View of some of the panel improved
- Improved Basic Authentication during Social engineering assessment over wireless network



Infernal-Wireless v2.6

This tool is created to aid the penetration testers in assessing wireless security.
Author is not responsible for misuse. Please read instructions thoroughly.  

Usage: `python InfernalWireless.py` (from the same folder where your code exists)

For any comments and suggestions please email on 1337[@]gmail[dot]com

## BUG Fixes:

1. Non ASCII SSID Name used to crash the software. It is fixed now
2. Warnings on the background is supressed
3. New Experimental Section is added but under development

## Release Notes:

1. Better User Interface
2. More Network device controls
3. Better SSL Strip Control
4. User / Access Point Deauthentication with auto channel detection of AP
5. Extra Wireless Scanner to detect Probe Requests, wireless Network scan and connections to AP detection
6. airgraph-ng suite is better implemented 
7. WPA2 Hacking UI is changed for better control over the attack
8. WPA2 Enterprise Hacking UI is changed for better control over the attack
9. Custome Fake Access Point is implemented. Freenet AP is deleted now. 
10. Check for software updates
11. Wiki page with video links to attacks tutorials
12. Folder are more structured
13. Check for prerequesites automatically

## FAQ:

### I have a problem with connecting to the Database

**Solution:**

*(Thanks to `@lightos` for this fix)*

There seem to be few issues with Database connectivity. The solution is to create a new user on the database and use that user for launching the tool. Follow the following steps.

1. Delete dbconnect.conf file from the Infernalwireless folder

2. Run the following command from your mysql console.

	mysql>`use mysql;`

	mysql>`CREATE USER 'root2'@'localhost' IDENTIFIED BY 'enter the new password here';`

	mysql>`GRANT ALL PRIVILEGES ON \*.\* TO 'root2'@'localhost' WITH GRANT OPTION;`

3. Try to run the tool again.


## Release Notes:

### New Features:

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


### Changes:

* Improved compatibility

* Report improvement

* Better NAT Rules


### Bug Fixes:

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

### Expected bugs:

* Wireless card might not be supported

* Might crash on Windows

* Freeze

* A lot of work to be done, but this tool is still being developed.

## Thanks and Credits:

* Special thanks to all my friends for comments and feedbacks. 
* Thank you zstyblik a lot for your patches, suggestions and improvements on the tool.

* Creators:

   * Aircrack

   * SSL Strip

   * Online Community

   * Others whom I forgot to mention.
