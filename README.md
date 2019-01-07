# [**Python**] Gaia Online Rally Bot
---
##### Contents
  0. [Planned Features](#planned-features)
  1. [Purpose](#purpose)
  2. [Login](#login)
  3. [Rally client](#client)
  4. [main.py](#main)


### 0. Planned Features
 - Fix the method 6 problem
 - Merge version 1.0 and version 2.0
 - Add a whitelist & ban list
 - Text-based User interface (TUI)
 - Control from Discord (maybe)
 - Finish README


### 1. Purpose
The point of this readme is to act as a self-reference and document as to what the source code for the bot does. If anybody else see's this then it should explain what the code does.

The readme will be broken down into several chunks going through each necessary script for the end product and also features that are being planned.


### 2. Login Script
The login script was created by Ryan completely, as a means to automate the insertion of the `gaia55_sid` before running the client script. The script makes use of the `Requests` library and `re`. The script comprises a `GaiaAuth` class which handles and processes the data needed to be inputted and returned.

```python
class GaiaAuth():
    def __init__(self, username, password):
        self.sess = requests.Session()
        msource = requests.get('http://www.gaiaonline.com/').text.replace('data-value', '')
```

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
             sys.exit(0)
```

This chunk of code goes through each of the inputs stored in `finputs` but starts from index 3 as the first 3 inputs that will be stored are not necessary to login. In the `try` loop, more regex is performed, assigned the found "names" and "values" into `ftempname` and `ftempvalue`. These are the inputs names and the inputs values. Before looping, the values are added into the dictionary with `ftempname` as the key, and `ftempvalue` as the value in to the params dictionary.

If the code fails, usually due to page not loading correctly, the code will quit using `sys.exit(0)`.  

```python
    self.sess.post('http://www.gaiaonline.com/auth/login/', params).headers
    sid = self.sess.cookies.get_dict()
    self.sid = sid['gaia55_sid']
```

The first line posts the data to the Gaia Online login page, calling only the headers for a faster response. The second line stores the cookies in a dictionary  which were created by logging in. The third line  assigns the specific cookie to `self.sid`

`gaia55_sid` is a cookie that Gaia Online uses to keep a session going. While the cookie is active, it means that you're logged in to the website and can access areas of the site that requires an account.

```python
print('SID:', self.sid)
```
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


### 3. Rally Client

The client aspects handles all the packets that are sent, and need to be sent to the Gaia servers. This section will be broken down into the different functions in the order of that I find most important.

**Due to differences in version 1.0 and 2.0 there may be some parts missing.**

```python
import asyncio
import logging
import sys
import time
import functools
import re
```

These are the necessary module that have to be imported. `asyncio` is required for the connection and the concurrency. It may not be required. `logging` is just for better visibility and was taken from the `asyncio` documentation.  `sys` is used for exits, and `time` is used for one packet which requires a timestamp. `functools` is used for applying arguments when creating the connection and `re` to parse the chat arguments, which will be shown.

```python
logging.basicConfig(
    level=logging.DEBUG,
    format='%(name)s: %(message)s',
    stream=sys.stderr
)
log = logging.getLogger('main')
event_loop = asyncio.get_event_loop()
```

Everything up until the last line just sets up logging for the client. However the last line starts the event loop from `asyncio`. An event loop reacts once an "event" has been triggered, e.g data being recieved.

### Packet decoding and encoding
The next two code blocks will not be in order of the overall script, but are necessary in order to understand how the packet data, which is received in bytes, is manipulated in order for it to be read more easily, and used by the script.

##### Decoding

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
      return data
```

the function `p_decode` takes the data that is received as bytes, and turns it into a list. it takes a packet as an argument before splitting it by control characters.

```python
data = []
transmission = packets.split('\x00')```
The function begins by creating and empty list and then splitting the current bytes into a list by trimming off the null byte, which Gaia uses to signal the true end of a packet.

```python
for packet in transmission:
    packets = packet.split('\x03')
    for part in packets:
        if part:
            thing = part.split('\x02')
```
From here we further iterate through the list of packets and split it by further characters, starting from `\x03`. From there however we check if `part` actually contains any data; Then we split it by `\x02`.

```python
for ky, vl in enumerate(thing):
    if '\x01' in vl:
        thing[ky] = vl.split('\x01')
```
Then, if the packet contains `\x01` we enumerate the "thing" and split at the index after enumerating. I've not seen this in use yet.

The last two lines simply append the data to a list and return the list. **Therefore all packets that we work with can either be lists or tuples.**

#### Encoding

Encoding in this case is turning "lists" of the data needed into byte-strings, that the server will accept.

```python
def p_encode(self, packets):
      '''
          Encodes a list made up of the packet requirements into a real 'packet', to be sent,
           that will be accepted by server. By joining each element in list with appropriate control character usng .join.
          '''
      data = ''
      packet = [str(x) for x in packets]  # turns all non str into str
      for ky, vl in enumerate(packet):
          if isinstance(vl, list):  # if value is a list
              packet[ky] = '\x01'.join(vl)
      data += '\x02'.join(packet) + '\x03\x00'
      return data.encode()
```

The line by line break down follows.

```python
data = ''
packet = [str(x) for x in packets]
```
We start by creating  an empty string, then using a list comprehension we make
sure that all items in the list are `str` types, rather than `int`.

```python
for ky, vl in enumerate(packet):
        if isinstance(vl, list):  # if value is a list
            packet[ky] = '\x01'.join(vl)
```
Then, like in the decode section, we have a special enumeration if there is a nested list
in the packet supplied. If this is the case we then begin joining those elements with the
`\x01` control character.

```python
data += '\x02'.join(packet) + '\x03\x00'
    return data.encode()
```
Then we begin adding data to the packet, after joining each item in the list with `\x02`
and ending the data with `\x03` and `\x00` control characters. The last line just returns the data
but in a `byte` type.

### Data Handling

```python
class RallyClient(asyncio.Protocol):
    def __init__(self, gaia55_sid, gaia_id, username, avatar_url, roomid, xy=('393', '932')):
```
To handle the data and the connection, we create an `asyncio.Protocol` class named `RallyClient` from `asyncio`
the `__init__` includes all the user data required to connect to the rally. `roomid` is the room number
which can be acquired from rally by typing `toggleip`.

```python
self.gaia55_sid = gaia55_sid
    self.gaia_id = gaia_id
    self.username = username
    self.avatar_url = avatar_url
    self.roomid = roomid
    self.xy1 = xy
    self.xy2 = ':'.join(xy)
```
All but the last lines are just assigning variables to the class, however the last line takes `xy` and then
joins it using a colon resulting in `393:932`. This is because certain packets, if not most require coords in
this format.

```python
self.log = logging.getLogger('RallyClient')
```
Creates a log named "RallyClient"

```python
self.flashpack = ['S55', 'FLASH', 1, 0, 2, 48]
    self.timestamp = [29, 1, self.gaia_id, 3, '-' + str(time.time())[0:-8]]
    self.method45 = [45, 2, 1, 1, 1, '', self.gaia_id, 0, 0, 1, 'btn0', self.avatar_url, self.username, self.gaia_id, 0, 8, 0,
               self.gaia55_sid, 0, 0]
```
These are variables for packets that are used during the handshaking when the connection is being made. **In version 2.0
these are tuples instead.** These packets are `p_encoded` later on.

```python
self.connected_users = {}
    self.inv_users = {}
    self.count = 0
    self.is_command = 0
    self.follow_id = ''
```
These variables are for keeping track of users, loops and commands. `self.connected_users` handles a userlist which is
contains `{ssid: [username, gaia_id, xy2]}` as a means to keep track of the connected users. `self.inv_users` is for
a dictionary also but inverted: `{username: [ssid, gaia_id, xy2]}`. This was done so that both dictionaries can
be called by each other. If there's a better way to do this, I haven't found it.

```python
async def pingu(self):
      """
      Sends a ping packet to severs every 40 seconds. Stops disconnection.
      """
      await asyncio.sleep(40)
      log = logging.getLogger('Ping!')
      self.transport.write(self.p_encode([62, '']))
      log.debug('Pong!')
      asyncio.ensure_future(self.pingu())
```
`pingu` is a function that sends a keep alive packet every 40 seconds in order to maintain a connection.
It uses `asyncio`'s `async` and `await` keywords in order to be done concurrently. The last line acts as a loop as it will recall the function, and there for have a constant loop that waits 40 seconds before writing a packet.
```python
self.transport.write(self.p_encode([62, '']))
```
This line sends the packet [62, ''], encodes it, and then sends the packet to the server.

```python
def connection_made(self, transport):
      self.transport = transport
      self.transport.write(self.p_encode(['S55', 'FLASH', 1, 0, 2, 48]))
      self.log.debug('Sent: flash packet')
      asyncio.ensure_future(self.pingu())
```
This is a function specific to the `asyncio.Protocol` class. It is called everytime
a connection is made, but only once. It takes `transport` which acts as the means to write data to the server.

```python
  self.transport.write(self.p_encode(['S55', 'FLASH', 1, 0, 2, 48]))
```

Because Gaia uses some sort of handshake by sending a packet of the flash version, I send the flash packet at the creation
of the connection. Data will not be received (or sent by the server) if this packet is not sent.

The last line simply initiates the pingu function loop.


**The next chunk of code will not include the whole block as it is too long.**

Next we will deal with data being received by the client.
```python
def data_received(self, data):
      ssid = ''
      self.data = self.p_decode(data.decode())
```
The `data_received` function is also a built in function from the `asyncio.Protocol` class. It is called every time data
is received by the connection. In the first line we create an `ssid` variable. Which is our specific session id for our connection to Rally, not the Gaia Online website (It is different to gaia55_sid).

```python
self.data = self.p_decode(data.decode())
```
This stores the data received, which is decoded from `byte` into `str` type, then broken down into a list by `p_decode`. This is done so that the specific chunks of data are more easily manipulated.

```python
for packet in self.data:

        if packet[0] == '1':
            ssid += packet[1]

        elif packet[0] == '10':
            cmsg = packet[4]
```
We then loop through self data with a for loop. Without this loop it the data is stored in a nested list `[[packet]]` which is why we loop through to get to the inside of the packet. From there, depending on what we need we will call the different items in the `packet` list.

```python
if packet[0] == '1':
    ssid += packet[1]
```
Here we are checking that IF the FIRST item in the packet is equal to 1. **For Gaia the first item in the packet is the method.**
then we will store the second item into the `ssid` variable. We know this is the `ssid` because it's method 1. All packet knowledge has come from Ryan and Wireshark packet captures.

The ssid is very important and is the packet sent in response to the `flashpack` sent upon the creation of the connection.

```python
elif packet[0] == '10':
    cmsg = packet[4]
```
Here we checking if the first item of the packet is 10, which represents a chat message. We then store the actual content of the message in `cmsg`, which is located at the index 4 of the packet.

We will be skipping of commands, which are under this loop and include it in a specific chapter.
