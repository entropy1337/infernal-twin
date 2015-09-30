import MySQLdb



def entercreds():
	print '*************** creating DB config file ************'
	username = raw_input('Enter the DB username: ')
	password = raw_input('Enter the password: ')

	#~ print 'Username is %s and Password is %s'%(username,password)
	mydbconfig = open('dbconnect.conf', 'w')
	mydbconfig.write(str(username) + '\n' + str(password)+ '\n')
	mydbconfig.close()



try: 
	
	dbfile = open('dbconnect.conf', 'r').readlines()

	db = MySQLdb.connect("localhost",str(dbfile[0]).replace('\n',''),str(dbfile[1]).replace('\n',''),"InfernalWireless")
	print 'I managed to connect'
	myconfig = open('dbconnect.conf','w')
	myconfig.write('root'+'\n'+''+'\n')
except:
	print 'dbconnect.conf doesn\'t exists or creds are incorrect'
	entercreds()
	dbfile = open('dbconnect.conf', 'r').readlines()
	
	num = 0
	print 'trying to connect'
	try:
		
		
		db = MySQLdb.connect(host="localhost", user=str(dbfile[0]).replace('\n',''), passwd=str(dbfile[1]).replace('\n',''), db="InfernalWireless")
		
	except:
		print 'username %s'%(dbfile[0])
		print 'password %s'%(dbfile[1])
		print 'Creds are not correct'  

	
#~ else:
	#~ entercreds()
	#~ dbfile = open('dbconnect.conf', 'r').readlines()
	#~ creds = []
	#~ num = 0
	#~ print 'trying to connect'
	#~ try:
		#~ db = MySQLdb.connect(host="localhost", user=dbfile[0], passwd=dbfile[1], db="InfernalWireless")
	#~ except:
		#~ print 'username %s'%(dbfile[0])
		#~ print 'p %s'%(dbfile[1])
		#~ print 'Creds are not correct'
	#~ 
	
	
	

