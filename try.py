import sys

try:
    f = open('myfile.txt')
    s = f.readline()
    i = int(s.strip())
    
except IOError as e:
    print "I/O error({0}): {1}".format(e.errno, e.strerror)

except ValueError:
    print "Could not convert data to an integer."

except:
    print "Unexpected error:", sys.exc_info()[0]
    raise

#except:
#			wx.MessageBox('Could not connect to DB', 'Warning/Error', wx.ICON_ERROR | wx.ICON_INFORMATION)
