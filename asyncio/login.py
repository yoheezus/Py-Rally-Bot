import requests

class GaiaAuth(): #start of auth class
    def __init__(self, username, password):
        self.fpostdata = 'username=' + username + '&password=' + password + '&'
        self.msource = self.request.get('http://gaiaonline.com/')
        self.finputs = #soon to be regex
