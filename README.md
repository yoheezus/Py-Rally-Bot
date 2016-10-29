# [**Python**] Gaia Online Rally Bot
---
##### Contents
  0. [Planned Features](#planned features)
  1. [Purpose](#purpose)
  2. [Login](#login)
  3. [Rally client](#client)
  4. [main.py](#main)

<a name="planned features"/>
### **Planned Features**
  -  [ ] Fix the method 6 problem
  -  [ ] Merge version 1.0 and version 2.0
  -  [ ] Add a whitelist & ban list
  -  [ ] Text-based User interface (TUI)
  -  [ ] Control from Discord (maybe)
  -  [ ] Finish README

<a name="purpose"/>
### 1. Purpose
The point of this readme is to act as a self-reference and document as to what the source code for the bot does. If anybody else see's this then it should explain what the code does.

The readme will be broken down into several chunks going through each necessary script for the end product and also features that are being planned.

<a name="login"/>
### 2. Login Script
The login script was created by Ryan completely, as a means to automate the insertion of the `gaia55_sid` before running the client script. The script makes use of the `Requests` library and `re`. The script comprises a `GaiaAuth` class which handles and processes the data needed to be inputted and returned.

```python
class GaiaAuth():
    def __init__(self, username, password):
        self.sess = requests.Session()
        msource = requests.get('http://www.gaiaonline.com/').text.replace('data-value', '')```

The creation of the class takes `username` and `password` as parameters. self.sess creates a `Requests` session. `msource` contains the data of a get request from `http://www.gaiaonline.com`, the `text.replace()` replaces all "data-values" with empty strings.

The next block deals with the searching and filling of login fields.
```python
    ftempname = ''
    ftempvalue = ''
    finputs = re.findall('<input([^>]+)>', msource)  # regex for getting the inputs
    params = {'username': username, 'password': password}
```
`ftempname` and `ftempvalue` are set to empty strings and will be used later on. `finputs` uses regex to find the input boxes within `msource`, the pages html.

 A dictionary is created which contains the username and password passed into the class. *"username"* and *"password"* are specific field names that are specified in the HTML.

 ```python
 for i in range(3, len(
             finputs)):  # loop from 3 to the length of our inputs from the regex, we don't need the first 3
         try:
             ftempname = re.search('name="([a-z0-9]{3,30})"', finputs[i]).group(1)  # Input name
             ftempvalue = re.search('value="([\.\a-z0-9]{25,32})"', finputs[i]).group(1)  # Input value
             params[ftempname] = ftempvalue  # adds form name and corresponding value to params dict
         except AttributeError:
             print('Try Again, Exiting.')
             sys.exit(0)```

This chunk of code goes through each of the inputs stored in `finputs` but starts from index 3 as the first 3 inputs that will be stored are not necessary to login. In the `try` loop, more regex is performed, assigned the found "names" and "values" into `ftempname` and `ftempvalue`. These are the inputs names and the inputs values. Before looping, the values are added into the dictionary with `ftempname` as the key, and `ftempvalue` as the value in to the params dictionary.

If the code fails, usually due to page not loading correctly, the code will quit using `sys.exit(0)`.  

```python
    self.sess.post('http://www.gaiaonline.com/auth/login/', params).headers
    sid = self.sess.cookies.get_dict()
    self.sid = sid['gaia55_sid']```

The first line posts the data to the Gaia Online login page, calling only the headers for a faster response. The second line stores the cookies in a dictionary  which were created by logging in. The third line  assigns the specific cookie to `self.sid`

`gaia55_sid` is a cookie that Gaia Online uses to keep a session going. While the cookie is active, it means that you're logged in to the website and can access areas of the site that requires an account.

```python
print('SID:', self.sid)```
simply prints the sesion id (sid).

The next part of the class deals with retrieving the information necessary to pass into the rally client.

```python
def method107(self):
      resp = self.sess.get('http://gaiaonline.com/chat/gsi/?m=[[107,[%22{}%22]]]&v=json'.format(self.sid))
      # Uses sid to make use of Gaia's API, enables us to automate other information.
      json = resp.json() # Loads the json, allows us to parse
      gaia_id = json[0][2]['gaia_id']
      avatar = json[0][2]['avatar']
      return gaia_id, avatar
       # Returns the info in this order. Remember to set vars in this order.
```

The first line uses the session, with the session id cookie, to retrieve data from the Gaia API. Method 107 uses the session id to return information using the gaia user id and the avatar url, the image of the avatar of a user.  

As the url includes `&v=json`, it results in the data being in json. Using `Requests` built in `json` function, it allows is to decode the data into python dictionaries, which we access and then return.

<a name="client" />
### 3. Rally Client

The client aspects handles all the packets that are sent, and need to be sent to the Gaia servers. This section will be broken down into the different functions in the order of that I find most important.

**Due to differences in version 1.0 and 2.0 there may be some parts missing.**

```python
import asyncio
import logging
import sys
import time
import functools
import re```

These are the necessary module that have to be imported. `asyncio` is required for the connection and the concurrency. It may not be required. `logging` is just for better visibility and was taken from the `asyncio` documentation.  `sys` is used for exits, and `time` is used for one packet which requires a timestamp. `functools` is used for applying arguments when creating the connection and `re` to parse the chat arguments, which will be shown.

```python
logging.basicConfig(
    level=logging.DEBUG,
    format='%(name)s: %(message)s',
    stream=sys.stderr
)
log = logging.getLogger('main')
event_loop = asyncio.get_event_loop()```

Everything up until the last line just sets up logging for the client. However the last line starts the event loop from `asyncio`. An event loop reacts once an "event" has been triggered, e.g data being recieved.

#### Packet decoding and encoding
The next two code blocks will not be in order of the overall script, but are necessary in order to understand how the packet data, which is received in bytes, is manipulated in order for it to be read more easily, and used by the script.

```python
def p_decode(self, packets):
      '''
      Decodes a packet into a list, making it easy to edit. Does this by splitting
      by control characters.
      '''
      data = []
      transmission = packets.split('\x00')
      for packet in transmission:
          packets = packet.split('\x03')
          for part in packets:
              if part:
                  thing = part.split('\x02')
                  for ky, vl in enumerate(thing):
                      if '\x01' in vl:
                          thing[ky] = vl.split('\x01')

                  data.append(thing)
      return data```

the function `p_decode` takes the data that is received as bytes, and turns it into a list. it takes a packet as an argument before splitting it by control characters.

```python
data = []
transmission = packets.split('\x00')```
The function begins by creating and empty list and then splitting the current bytes into a list by trimming off the null byte, which Gaia uses to signal the true end of a packet.
