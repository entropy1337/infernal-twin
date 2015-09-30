********************
INFERNAL WIRELESS
********************

This is the tool created to automate Evil Twin attack and capturing public and guest credentials of Access Point

What this tool will do ? 

1. Set up monitoring interface
2. Set up DB
3. Scan wireless network in the range
4. Connect to the network selected SSID 
5. Obtain login page of authentication
6. Modify the login page with attacker controlled php script to obtain the credentials
7. Set up Apache Server and serve fake login page
8. Give a victim an IP 
9. Set up NAT table
10. Dump the traffic

How to execute? 

1. Login to the target SSID 
2. Copy the login page of the public access point and place under /var/www/login.html
3. disconnect from target SSID
4. Run python infernal-wireless.py

Note: 

This tool might need modifications and contributions are welcome. 

P.S.

You need to modify the creds.php script. Put your mysql DB password. 


