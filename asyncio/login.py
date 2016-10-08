import requests
import re

class GaiaAuth():
    def __init__(self, username, password):
        fpostdata = "'username':'" + username + "','password':'" + password + "'" #Start of out post data
        msource = requests.get('http://gaiaonline.com/').text #Send HTTP GET request to http://gaiaonline.com/
        ftempname = ''
        ftempvalue = ''
        finputs = re.findall('<input([^>]+)>', msource) #regex for getting the inputs
        
        for i in range(3, len(finputs)): #loop from 3 to the length of our inputs from the regex, we don't need the first 3
            ftempname = re.search('name="(.*?)"', finputs[i]).group(1) #Input name
            ftempvalue = re.search('value="(.*?)"', finputs[i]).group(1) #Input value
            fpostdata += ",'" + ftempname + "':'" + ftempvalue + "'" #Finally compose it all
        #rheaders = requests.post('http://www.gaiaonline.com/auth/login/', data = {fpostdata}).headers
            
        print(fpostdata) #Our necessary post data.


GaiaAuth('','') #Do nothing with this yet
