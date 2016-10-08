import requests
import re

class GaiaAuth():
    def __init__(self, username, password):
        sess = requests.Session()
        msource = requests.get('http://gaiaonline.com/').text.replace('data-value', '') #Send HTTP GET request to http://gaiaonline.com/
        ftempname = ''
        ftempvalue = ''
        finputs = re.findall('<input([^>]+)>', msource) #regex for getting the inputs
        params = {'username' : username, 'password' : password}
        
        for i in range(3, len(finputs)): #loop from 3 to the length of our inputs from the regex, we don't need the first 3
            #print(finputs[i])
            ftempname = re.search('name="([a-z0-9]{3,30})"', finputs[i]).group(1) #Input name
            ftempvalue = re.search('value="([\.\a-z0-9]{25,32})"', finputs[i]).group(1) #Input value
            params[ftempname] = ftempvalue # adds form name and corresponding value to params dict 
        sess.post('http://www.gaiaonline.com/auth/login/', params).headers
        sid = sess.cookies.get_dict()
        sid = sid['gaia55_sid']
        
        print('SID:', sid)
        
GaiaAuth('username','password') #Do nothing with this yet
