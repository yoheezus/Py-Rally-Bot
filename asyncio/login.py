import requests
import re

class GaiaAuth():
    def __init__(self, username, password):
        msource = requests.get('http://gaiaonline.com/').text.replace('data-value', '') #Send HTTP GET request to http://gaiaonline.com/
        ftempname = ''
        ftempvalue = ''
        finputs = re.findall('<input([^>]+)>', msource) #regex for getting the inputs
        
        for i in range(3, len(finputs)): #loop from 3 to the length of our inputs from the regex, we don't need the first 3
            #print(finputs[i])
            ftempname = re.search('name="([a-z0-9]{3,30})"', finputs[i]).group(1) #Input name
            ftempvalue = re.search('value="([\.\a-z0-9]{25,32})"', finputs[i]).group(1) #Input value
            fpostdata += ftempname + ftempvalue #Finally compose it all
        fpostdata = {'username' : username, 'password' : password, }
    '''   
    rheaders = requests.post('http://www.gaiaonline.com/auth/login/', data = fpostdata).headers
        sid = re.search('gaia55_sid=([a-z0-9]{48})', rheaders['Set-Cookie'])
        if sid:
            print('SID: ' + rheaders['Set-Cookie']) #Our necessary post data.
        else:
            print('oh no!')

'''
GaiaAuth('username','password') #Do nothing with this yet
