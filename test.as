dbfile = open('dbconnect.conf', 'r').readlines()
dbfile.close()

user=str(dbfile[0]).replace('\n',''), passwd=str(dbfile[1]).replace('\n','')
