import requests
import re

class GaiaAuth():
    def __init__(self, username, password):
        fpostdata = 'username=' + username + '&password=' + password + '&'
        msource = requests.get('http://gaiaonline.com/').text
        print(msource)
        finputs = re.findall('<input([^>]+)>', msource)
        for i in range(3, len(finputs)):
            print(finputs)


GaiaAuth('','')
