import urllib2

class SmartRedirectHandler(urllib2.HTTPRedirectHandler):     
    def http_error_301(self, req, fp, code, msg, headers):  
        result = urllib2.HTTPRedirectHandler.http_error_301( self, req, fp, code, msg, headers)              
        result.status = headers                                 
        return result                                       

    def http_error_302(self, req, fp, code, msg, headers):   
        result = urllib2.HTTPRedirectHandler.http_error_302(self, req, fp, code, msg, headers)              
        result.status = headers                              
        return result   
