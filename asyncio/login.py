import requests
import re

class GaiaAuth():
    def __init__(self, username, password):
        sess = requests.Session()
        msource = requests.get('http://gaiaonline.com/').text.replace('data-value', '') #Send HTTP GET request to http://gaiaonline.com/
        ftempname = ''
        ftempvalue = ''
        finputs = re.findall('<input([^>]+)>', msource) #Regex for getting the inputs
        params = {'username' : username, 'password' : password}
        
        for i in range(3, len(finputs)): #Loop from 3 to the length of our inputs from the regex, we don't need the first 3
            #print(finputs[i])
            try:    
                ftempname = re.search('name="([a-z0-9]{3,30})"', finputs[i]).group(1)  # Input name    
                ftempvalue = re.search('value="([\.\a-z0-9]{25,32})"', finputs[i]).group(1)  # Input value    
                params[ftempname] = ftempvalue  # Adds form name and corresponding value to params dict
            except AttributeError:    
                print('Try Again')    
                break
        sess.post('http://www.gaiaonline.com/auth/login/', params).headers #Send HTTP POST request with our necessary post data.
        sid = sess.cookies.get_dict() #Obtain a dictionary
        sid = sid['gaia55_sid'] #sid now has the session value
        
        print('SID:', sid)
        
        def method107(self):    
            resp = self.sess.get('http://gaiaonline.com/chat/gsi/?m=[[107,[%22{}%22]]]&v=json'.format(self.sid))    # Uses sid to make use of Gaia's API, enables us to automate other information.    
            json = resp.json() # Loads the json, allows us to parse    
            gaia_id = json[0][2]['gaia_id']    
            avatar = json[0][2]['avatar']    
            return gaia_id, avatar # Returns the info in this order. Remember to set vars in this order.

if __name__ == '__main__':
    auth = GaiaAuth('username','password') #Do nothing with this yet
    auth.method107()
    
